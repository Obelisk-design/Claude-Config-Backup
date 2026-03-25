# -*- coding: utf-8 -*-
"""GitHub storage implementation for backup files"""

import base64
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from github import Github, RateLimitExceededException
from github.Repository import Repository
from storage.base import StorageBase
from core.exceptions import BackupError, RateLimitError, RestoreError
from utils.logger import logger


class GitHubStorage(StorageBase):
    """GitHub storage provider for backing up files to a GitHub repository"""

    BACKUP_DIR = "backups"
    DEFAULT_REPO_NAME = "claude-config-backup"

    def __init__(self, token: str, repo_name: Optional[str] = None):
        """Initialize GitHub storage

        Args:
            token: GitHub personal access token
            repo_name: Optional repository name (defaults to DEFAULT_REPO_NAME)
        """
        self.token = token
        self.repo_name = repo_name or self.DEFAULT_REPO_NAME
        self._github: Optional[Github] = None
        self._repo: Optional[Repository] = None
        logger.info(f"Initialized GitHubStorage with repo: {self.repo_name}")

    @property
    def github(self) -> Github:
        """Get or create GitHub client"""
        if self._github is None:
            self._github = Github(self.token)
        return self._github

    def get_or_create_repo(self) -> Repository:
        """Get or create the backup repository

        Returns:
            Repository object

        Raises:
            BackupError: If unable to get or create repository
        """
        if self._repo is not None:
            return self._repo

        try:
            # Try to get existing repo
            user = self.github.get_user()
            try:
                self._repo = user.get_repo(self.repo_name)
                logger.info(f"Found existing repository: {self.repo_name}")
                return self._repo
            except RateLimitExceededException:
                raise
            except Exception:
                self._repo = user.create_repo(
                    name=self.repo_name,
                    private=True,
                    description="Claude Code configuration backup repository",
                    auto_init=True
                )
                logger.info(f"Created new private repository: {self.repo_name}")
                return self._repo
        except RateLimitExceededException as e:
            reset_time = e.headers.get('X-RateLimit-Reset', 0)
            raise RateLimitError(reset_time=int(reset_time))
        except Exception as e:
            logger.error(f"Failed to get or create repository: {e}")
            raise BackupError(f"Failed to get or create repository: {e}")

    def _get_full_path(self, remote_path: str) -> str:
        """Get full path including backup directory"""
        return f"{self.BACKUP_DIR}/{remote_path}"

    def _extract_created_at(self, file_path: str) -> Optional[str]:
        stem = Path(file_path).stem
        try:
            return datetime.strptime(stem, "%Y%m%d_%H%M%S").isoformat()
        except ValueError:
            return None

    def _build_file_metadata(self, content) -> Dict[str, Any]:
        file_path = content.path
        if file_path.startswith(self.BACKUP_DIR + "/"):
            file_path = file_path[len(self.BACKUP_DIR) + 1:]

        return {
            "name": Path(file_path).name,
            "path": file_path,
            "size": getattr(content, "size", 0),
            "created_at": self._extract_created_at(file_path),
            "download_url": getattr(content, "download_url", None),
        }

    def _list_directory(self, repo: Repository, prefix: str = "") -> List[Dict[str, Any]]:
        backup_dir = self._get_full_path(prefix).rstrip("/")
        files: List[Dict[str, Any]] = []
        contents = repo.get_contents(backup_dir)

        if not isinstance(contents, list):
            contents = [contents]

        for content in contents:
            if content.type == "file":
                files.append(self._build_file_metadata(content))
            elif content.type == "dir":
                subdir_prefix = content.path[len(self.BACKUP_DIR) + 1:]
                files.extend(self._list_directory(repo, subdir_prefix + "/"))

        return files

    def upload(self, local_path: str, remote_path: str) -> bool:
        """Upload a file to the GitHub repository

        Args:
            local_path: Path to the local file
            remote_path: Path where the file should be stored remotely

        Returns:
            True if upload was successful

        Raises:
            BackupError: If upload fails
            RateLimitError: If GitHub rate limit is exceeded
        """
        try:
            repo = self.get_or_create_repo()
            full_path = self._get_full_path(remote_path)

            # Read file content
            with open(local_path, 'rb') as f:
                content = f.read()

            # Check if file exists
            try:
                existing_file = repo.get_contents(full_path)
                repo.update_file(
                    path=full_path,
                    message=f"Update backup: {remote_path}",
                    content=content,
                    sha=existing_file.sha
                )
                logger.info(f"Updated file: {full_path}")
            except RateLimitExceededException:
                raise
            except Exception:
                repo.create_file(
                    path=full_path,
                    message=f"Create backup: {remote_path}",
                    content=content
                )
                logger.info(f"Created file: {full_path}")

            return True

        except RateLimitExceededException as e:
            reset_time = e.headers.get('X-RateLimit-Reset', 0)
            logger.warning(f"Rate limit exceeded, resets at {reset_time}")
            raise RateLimitError(reset_time=int(reset_time))
        except BackupError:
            raise
        except Exception as e:
            logger.error(f"Failed to upload file {local_path}: {e}")
            raise BackupError(f"Failed to upload file: {e}")

    def download(self, remote_path: str, local_path: str) -> bool:
        """Download a file from the GitHub repository

        Args:
            remote_path: Path to the remote file
            local_path: Path where the file should be saved locally

        Returns:
            True if download was successful

        Raises:
            RestoreError: If download fails
            RateLimitError: If GitHub rate limit is exceeded
        """
        try:
            repo = self.get_or_create_repo()
            full_path = self._get_full_path(remote_path)

            # Get file content
            file_content = repo.get_contents(full_path)

            # Decode and write to local file
            content = base64.b64decode(file_content.content)
            with open(local_path, 'wb') as f:
                f.write(content)

            logger.info(f"Downloaded file: {full_path} to {local_path}")
            return True

        except RateLimitExceededException as e:
            reset_time = e.headers.get('X-RateLimit-Reset', 0)
            logger.warning(f"Rate limit exceeded, resets at {reset_time}")
            raise RateLimitError(reset_time=int(reset_time))
        except RestoreError:
            raise
        except Exception as e:
            logger.error(f"Failed to download file {remote_path}: {e}")
            raise RestoreError(f"Failed to download file: {e}")

    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List backup files in the repository

        Args:
            prefix: Optional prefix to filter files

        Returns:
            List of remote file metadata
        """
        try:
            repo = self.get_or_create_repo()
            try:
                files = self._list_directory(repo, prefix)
            except RateLimitExceededException:
                raise
            except Exception:
                files = []

            files.sort(
                key=lambda item: item.get("created_at") or item["name"],
                reverse=True
            )

            logger.info(f"Listed {len(files)} files with prefix '{prefix}'")
            return files

        except RateLimitExceededException as e:
            reset_time = e.headers.get('X-RateLimit-Reset', 0)
            logger.warning(f"Rate limit exceeded, resets at {reset_time}")
            raise RateLimitError(reset_time=int(reset_time))
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []

    def delete(self, remote_path: str) -> bool:
        """Delete a file from the GitHub repository

        Args:
            remote_path: Path to the remote file

        Returns:
            True if deletion was successful

        Raises:
            BackupError: If deletion fails
            RateLimitError: If GitHub rate limit is exceeded
        """
        try:
            repo = self.get_or_create_repo()
            full_path = self._get_full_path(remote_path)

            # Get file to get its SHA
            file_content = repo.get_contents(full_path)

            # Delete file
            repo.delete_file(
                path=full_path,
                message=f"Delete backup: {remote_path}",
                sha=file_content.sha
            )

            logger.info(f"Deleted file: {full_path}")
            return True

        except RateLimitExceededException as e:
            reset_time = e.headers.get('X-RateLimit-Reset', 0)
            logger.warning(f"Rate limit exceeded, resets at {reset_time}")
            raise RateLimitError(reset_time=int(reset_time))
        except BackupError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete file {remote_path}: {e}")
            raise BackupError(f"Failed to delete file: {e}")

    def get_file_url(self, remote_path: str) -> Optional[str]:
        """Get the URL for a remote file

        Args:
            remote_path: Path to the remote file

        Returns:
            URL to access the file, or None if not available
        """
        try:
            repo = self.get_or_create_repo()
            full_path = self._get_full_path(remote_path)

            file_content = repo.get_contents(full_path)
            return file_content.download_url

        except RateLimitExceededException as e:
            reset_time = e.headers.get('X-RateLimit-Reset', 0)
            logger.warning(f"Rate limit exceeded, resets at {reset_time}")
            raise RateLimitError(reset_time=int(reset_time))
        except Exception as e:
            logger.error(f"Failed to get file URL for {remote_path}: {e}")
            return None
