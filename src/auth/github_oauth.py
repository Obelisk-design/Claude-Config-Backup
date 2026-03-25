# -*- coding: utf-8 -*-
"""GitHub OAuth 认证模块"""

import json
import secrets
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs, urlparse

import requests

from core.exceptions import AuthenticationError, TokenExpiredError
from utils.logger import logger


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """OAuth 回调处理器"""

    callback_received = None
    auth_code = None
    auth_state = None
    error = None

    def log_message(self, format, *args):
        """禁用默认日志"""
        pass

    def do_GET(self):
        """处理 GET 请求"""
        parsed = urlparse(self.path)

        if parsed.path != "/callback":
            self.send_error(404)
            return

        query = parse_qs(parsed.query)

        if "error" in query:
            self.error = query["error"][0]
            self.send_response(400)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Authentication Failed</h1></body></html>")
        elif "code" in query:
            self.auth_code = query["code"][0]
            self.auth_state = query.get("state", [None])[0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>Authentication Successful!</h1>"
                b"<p>You can close this window now.</p></body></html>"
            )
        else:
            self.send_error(400)

        OAuthCallbackHandler.callback_received.set()


class GitHubOAuth:
    """GitHub OAuth 认证"""

    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_API = "https://api.github.com/user"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_port: int = 18080,
        scope: str = "repo,read:user"
    ):
        """初始化 GitHub OAuth

        Args:
            client_id: GitHub OAuth App Client ID
            client_secret: GitHub OAuth App Client Secret
            redirect_port: 本地回调服务器端口
            scope: OAuth 权限范围
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_port = redirect_port
        self.scope = scope
        self.redirect_uri = f"http://localhost:{redirect_port}/callback"

    def get_authorization_url(self, state: str = None) -> str:
        """生成 OAuth 授权 URL

        Args:
            state: 可选的状态参数，用于防止 CSRF 攻击

        Returns:
            授权 URL
        """
        if state is None:
            state = secrets.token_urlsafe(16)

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "state": state,
        }

        url = f"{self.AUTHORIZE_URL}?{urlencode(params)}"
        logger.info(f"Generated authorization URL with state: {state}")
        return url

    def exchange_code(self, code: str) -> str:
        """使用授权码交换访问令牌

        Args:
            code: GitHub 返回的授权码

        Returns:
            access_token 字符串

        Raises:
            AuthenticationError: 认证失败
        """
        # 确保 code 是纯字符串，如果传入了 tuple (比如之前解包失败的情况残留) 则取第一个元素
        if isinstance(code, tuple) or isinstance(code, list):
            code = code[0]

        # 强制转换为字符串并清理
        code = str(code).strip()

        data = {
            "client_id": self.client_id.strip() if self.client_id else "",
            "client_secret": self.client_secret.strip() if self.client_secret else "",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }

        headers = {
            "Accept": "application/json",
        }

        try:
            logger.info(f"Exchanging code for token with client_id: {data['client_id'][:5]}... redirect_uri: {data['redirect_uri']}")
            response = requests.post(self.TOKEN_URL, data=data, headers=headers)
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                logger.error(f"OAuth error: {result['error']}")
                raise AuthenticationError(f"OAuth error: {result.get('error_description', result['error'])}")

            logger.info("Successfully exchanged code for access token")

            # 如果 access_token 不在顶层，检查是否有可能 GitHub 返回格式变化
            if "access_token" not in result:
                logger.error(f"Unexpected token response format: {result}")
                raise AuthenticationError("Failed to get access token from response")

            return result.get("access_token", "")

        except requests.RequestException as e:
            logger.error(f"Failed to exchange code: {e}")
            raise AuthenticationError(f"Failed to exchange code: {e}")

    def get_user_info(self, token: str) -> dict:
        """获取 GitHub 用户信息

        Args:
            token: 访问令牌

        Returns:
            用户信息字典

        Raises:
            AuthenticationError: 认证失败
            TokenExpiredError: Token 过期
        """
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        try:
            response = requests.get(self.USER_API, headers=headers)

            if response.status_code == 401:
                raise TokenExpiredError("Token is invalid or expired")

            response.raise_for_status()
            user_info = response.json()
            logger.info(f"Retrieved user info for: {user_info.get('login')}")
            return user_info

        except requests.RequestException as e:
            logger.error(f"Failed to get user info: {e}")
            raise AuthenticationError(f"Failed to get user info: {e}")

    def start_callback_server(self, timeout: int = 300) -> tuple:
        """启动本地回调服务器并等待授权

        Args:
            timeout: 超时时间（秒）

        Returns:
            (auth_code, state) 元组

        Raises:
            AuthenticationError: 认证失败或超时
        """
        try:
            # 尝试先启动服务器并捕获可能的端口占用异常
            server_address = ("", self.redirect_port)
            httpd = HTTPServer(server_address, OAuthCallbackHandler)
        except OSError as e:
            logger.error(f"Failed to start callback server on port {self.redirect_port}: {e}")
            raise AuthenticationError(f"回调端口 {self.redirect_port} 被占用或无法绑定。请检查设置。")

        OAuthCallbackHandler.callback_received = threading.Event()
        OAuthCallbackHandler.auth_code = None
        OAuthCallbackHandler.auth_state = None
        OAuthCallbackHandler.error = None

        server_thread = threading.Thread(target=httpd.handle_request)
        server_thread.daemon = True

        # 先启动服务器，再打开浏览器，避免浏览器过快重定向导致连接被拒
        server_thread.start()
        auth_url = self.get_authorization_url()
        logger.info(f"Opening browser for OAuth authorization...")
        webbrowser.open(auth_url)

        try:
            if not OAuthCallbackHandler.callback_received.wait(timeout=timeout):
                raise AuthenticationError("OAuth callback timed out")
        finally:
            # 无论是否超时或发生异常，都必须确保关闭服务器，释放端口
            httpd.server_close()

        if OAuthCallbackHandler.error:
            raise AuthenticationError(f"OAuth error: {OAuthCallbackHandler.error}")

        return OAuthCallbackHandler.auth_code, OAuthCallbackHandler.auth_state
