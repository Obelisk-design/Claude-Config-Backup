# tests/test_github_oauth.py
import pytest
import sys
sys.path.insert(0, 'src')

from unittest.mock import patch, MagicMock
from auth.github_oauth import GitHubOAuth, OAuthCallbackHandler
from core.exceptions import AuthenticationError, TokenExpiredError


class TestGitHubOAuth:
    """GitHub OAuth 测试类"""

    @pytest.fixture
    def oauth(self):
        """创建 OAuth 实例"""
        return GitHubOAuth(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_port=18080,
            scope="repo,read:user"
        )

    def test_generate_auth_url(self, oauth):
        """测试生成授权 URL - 验证 URL 包含 client_id 和 scope"""
        url = oauth.get_authorization_url(state="test_state")

        assert "https://github.com/login/oauth/authorize" in url
        assert "client_id=test_client_id" in url
        assert "scope=repo%2Cread%3Auser" in url
        assert "state=test_state" in url
        assert "redirect_uri=http%3A%2F%2Flocalhost%3A18080%2Fcallback" in url

    def test_generate_auth_url_auto_state(self, oauth):
        """测试自动生成 state 参数"""
        url = oauth.get_authorization_url()

        assert "state=" in url
        # state 应该是自动生成的随机字符串

    @patch('requests.post')
    def test_exchange_code(self, mock_post, oauth):
        """测试交换授权码 - mock requests.post"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "token_type": "bearer",
            "scope": "repo,read:user"
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = oauth.exchange_code("test_code")

        assert result == "test_access_token"

        # 验证调用参数
        mock_post.assert_called_once_with(
            oauth.TOKEN_URL,
            data={
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "code": "test_code",
                "redirect_uri": oauth.redirect_uri,
            },
            headers={"Accept": "application/json"}
        )

    @patch('requests.post')
    def test_exchange_code_error(self, mock_post, oauth):
        """测试交换授权码失败"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": "bad_verification_code",
            "error_description": "The code passed is incorrect or expired."
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        with pytest.raises(AuthenticationError):
            oauth.exchange_code("invalid_code")

    @patch('requests.get')
    def test_get_user_info(self, mock_get, oauth):
        """测试获取用户信息 - mock requests.get"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "login": "testuser",
            "id": 12345,
            "name": "Test User",
            "email": "test@example.com"
        }
        mock_response.raise_for_status = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        user_info = oauth.get_user_info("test_token")

        assert user_info["login"] == "testuser"
        assert user_info["id"] == 12345

        # 验证调用参数
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "https://api.github.com/user" in str(call_args[0])
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_token"

    @patch('requests.get')
    def test_get_user_info_token_expired(self, mock_get, oauth):
        """测试 Token 过期"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with pytest.raises(TokenExpiredError):
            oauth.get_user_info("expired_token")


class TestOAuthCallbackHandler:
    """OAuth 回调处理器测试"""

    def test_callback_handler_attributes(self):
        """测试回调处理器属性"""
        assert hasattr(OAuthCallbackHandler, 'callback_received')
        assert hasattr(OAuthCallbackHandler, 'auth_code')
        assert hasattr(OAuthCallbackHandler, 'auth_state')
        assert hasattr(OAuthCallbackHandler, 'error')


class TestGitHubOAuthUrls:
    """测试 URL 常量"""

    def test_authorize_url(self):
        """测试授权 URL 常量"""
        assert GitHubOAuth.AUTHORIZE_URL == "https://github.com/login/oauth/authorize"

    def test_token_url(self):
        """测试 Token URL 常量"""
        assert GitHubOAuth.TOKEN_URL == "https://github.com/login/oauth/access_token"

    def test_user_api(self):
        """测试用户 API URL 常量"""
        assert GitHubOAuth.USER_API == "https://api.github.com/user"