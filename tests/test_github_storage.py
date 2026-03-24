# tests/test_github_storage.py
import pytest
import sys
import base64
from unittest.mock import Mock, MagicMock, patch, mock_open

sys.path.insert(0, 'src')

from storage.github_storage import GitHubStorage
from core.exceptions import BackupError, RateLimitError, RestoreError


class TestGitHubStorage:
    """Tests for GitHubStorage class"""

    @pytest.fixture
    def mock_github(self):
        """Create mock GitHub client"""
        with patch('storage.github_storage.Github') as mock:
            yield mock

    @pytest.fixture
    def mock_repo(self):
        """Create mock repository"""
        repo = Mock()
        repo.name = "claude-config-backup"
        repo.private = True
        return repo

    @pytest.fixture
    def mock_user(self, mock_repo):
        """Create mock user"""
        user = Mock()
        user.get_repo.return_value = mock_repo
        user.create_repo.return_value = mock_repo
        return user

    @pytest.fixture
    def storage(self, mock_github, mock_user):
        """Create GitHubStorage instance with mocked dependencies"""
        mock_github.return_value.get_user.return_value = mock_user
        storage = GitHubStorage(token="test_token")
        return storage

    def test_init(self):
        """Test initialization of GitHubStorage"""
        storage = GitHubStorage(token="test_token")
        assert storage.token == "test_token"
        assert storage.repo_name == GitHubStorage.DEFAULT_REPO_NAME

    def test_init_with_custom_repo_name(self):
        """Test initialization with custom repo name"""
        storage = GitHubStorage(token="test_token", repo_name="custom-repo")
        assert storage.token == "test_token"
        assert storage.repo_name == "custom-repo"

    def test_get_or_create_repo_existing(self, mock_github, mock_user, mock_repo):
        """Test getting an existing repository"""
        mock_github.return_value.get_user.return_value = mock_user
        mock_user.get_repo.return_value = mock_repo

        storage = GitHubStorage(token="test_token")
        repo = storage.get_or_create_repo()

        assert repo == mock_repo
        mock_user.get_repo.assert_called_once_with(GitHubStorage.DEFAULT_REPO_NAME)
        mock_user.create_repo.assert_not_called()

    def test_get_or_create_repo_create_new(self, mock_github, mock_user, mock_repo):
        """Test creating a new repository when it doesn't exist"""
        mock_github.return_value.get_user.return_value = mock_user
        mock_user.get_repo.side_effect = Exception("Repo not found")
        mock_user.create_repo.return_value = mock_repo

        storage = GitHubStorage(token="test_token")
        repo = storage.get_or_create_repo()

        assert repo == mock_repo
        mock_user.create_repo.assert_called_once()

    def test_upload_file_new(self, storage, mock_repo):
        """Test uploading a new file"""
        # Setup mock for get_or_create_repo
        storage._repo = mock_repo

        # Mock file doesn't exist
        mock_repo.get_contents.side_effect = Exception("File not found")

        # Mock create_file
        mock_repo.create_file.return_value = {"content": Mock()}

        # Mock file read
        with patch('builtins.open', mock_open(read_data=b'test content')):
            result = storage.upload("/local/path/file.txt", "file.txt")

        assert result is True
        mock_repo.create_file.assert_called_once()

    def test_upload_file_update(self, storage, mock_repo):
        """Test updating an existing file"""
        # Setup mock for get_or_create_repo
        storage._repo = mock_repo

        # Mock file exists
        existing_file = Mock()
        existing_file.sha = "abc123"
        mock_repo.get_contents.return_value = existing_file

        # Mock update_file
        mock_repo.update_file.return_value = {"content": Mock()}

        # Mock file read
        with patch('builtins.open', mock_open(read_data=b'test content')):
            result = storage.upload("/local/path/file.txt", "file.txt")

        assert result is True
        mock_repo.update_file.assert_called_once()

    def test_upload_file_rate_limit(self, storage, mock_repo):
        """Test rate limit handling during upload"""
        from github import RateLimitExceededException

        # Setup mock for get_or_create_repo
        storage._repo = mock_repo

        # Mock rate limit exception
        mock_repo.get_contents.side_effect = RateLimitExceededException(
            403,
            {"message": "Rate limit exceeded"},
            {"X-RateLimit-Reset": "1711281000"}
        )

        with patch('builtins.open', mock_open(read_data=b'test content')):
            with pytest.raises(RateLimitError) as exc_info:
                storage.upload("/local/path/file.txt", "file.txt")

            assert exc_info.value.reset_time == 1711281000

    def test_download_file(self, storage, mock_repo):
        """Test downloading a file"""
        # Setup mock for get_or_create_repo
        storage._repo = mock_repo

        # Mock file content
        file_content = Mock()
        file_content.content = base64.b64encode(b'test content').decode('utf-8')
        mock_repo.get_contents.return_value = file_content

        # Mock file write
        with patch('builtins.open', mock_open()) as mock_file:
            result = storage.download("file.txt", "/local/path/file.txt")

        assert result is True
        mock_repo.get_contents.assert_called_once()

    def test_download_file_not_found(self, storage, mock_repo):
        """Test downloading a file that doesn't exist"""
        # Setup mock for get_or_create_repo
        storage._repo = mock_repo

        # Mock file not found
        mock_repo.get_contents.side_effect = Exception("File not found")

        with patch('builtins.open', mock_open()):
            with pytest.raises(RestoreError):
                storage.download("file.txt", "/local/path/file.txt")

    def test_list_files(self, storage, mock_repo):
        """Test listing files"""
        # Setup mock for get_or_create_repo
        storage._repo = mock_repo

        # Mock directory contents
        file1 = Mock()
        file1.type = "file"
        file1.path = "backups/config.json"

        file2 = Mock()
        file2.type = "file"
        file2.path = "backups/settings.json"

        mock_repo.get_contents.return_value = [file1, file2]

        files = storage.list_files()

        assert len(files) == 2
        assert "config.json" in files
        assert "settings.json" in files

    def test_list_files_empty(self, storage, mock_repo):
        """Test listing files when directory is empty or doesn't exist"""
        # Setup mock for get_or_create_repo
        storage._repo = mock_repo

        # Mock empty directory
        mock_repo.get_contents.side_effect = Exception("Directory not found")

        files = storage.list_files()

        assert files == []

    def test_list_files_with_prefix(self, storage, mock_repo):
        """Test listing files with prefix filter"""
        # Setup mock for get_or_create_repo
        storage._repo = mock_repo

        # Mock directory contents
        file1 = Mock()
        file1.type = "file"
        file1.path = "backups/subdir/config.json"

        mock_repo.get_contents.return_value = [file1]

        files = storage.list_files("subdir/")

        assert len(files) == 1
        assert "subdir/config.json" in files

    def test_delete_file(self, storage, mock_repo):
        """Test deleting a file"""
        # Setup mock for get_or_create_repo
        storage._repo = mock_repo

        # Mock file content
        file_content = Mock()
        file_content.sha = "abc123"
        mock_repo.get_contents.return_value = file_content

        result = storage.delete("file.txt")

        assert result is True
        mock_repo.delete_file.assert_called_once()

    def test_delete_file_not_found(self, storage, mock_repo):
        """Test deleting a file that doesn't exist"""
        # Setup mock for get_or_create_repo
        storage._repo = mock_repo

        # Mock file not found
        mock_repo.get_contents.side_effect = Exception("File not found")

        with pytest.raises(BackupError):
            storage.delete("file.txt")

    def test_get_file_url(self, storage, mock_repo):
        """Test getting file URL"""
        # Setup mock for get_or_create_repo
        storage._repo = mock_repo

        # Mock file content
        file_content = Mock()
        file_content.download_url = "https://raw.githubusercontent.com/user/repo/main/backups/file.txt"
        mock_repo.get_contents.return_value = file_content

        url = storage.get_file_url("file.txt")

        assert url == "https://raw.githubusercontent.com/user/repo/main/backups/file.txt"

    def test_get_file_url_not_found(self, storage, mock_repo):
        """Test getting URL for a file that doesn't exist"""
        # Setup mock for get_or_create_repo
        storage._repo = mock_repo

        # Mock file not found
        mock_repo.get_contents.side_effect = Exception("File not found")

        url = storage.get_file_url("file.txt")

        assert url is None

    def test_rate_limit_error(self, mock_github, mock_user):
        """Test RateLimitError is raised properly"""
        from github import RateLimitExceededException

        mock_github.return_value.get_user.side_effect = RateLimitExceededException(
            403,
            {"message": "Rate limit exceeded"},
            {"X-RateLimit-Reset": "1711281000"}
        )

        storage = GitHubStorage(token="test_token")

        with pytest.raises(RateLimitError) as exc_info:
            storage.get_or_create_repo()

        assert exc_info.value.reset_time == 1711281000