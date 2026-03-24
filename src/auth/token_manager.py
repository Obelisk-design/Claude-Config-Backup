# -*- coding: utf-8 -*-
"""Token 管理模块"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

from security.crypto import Crypto
from utils.logger import logger


class TokenManager:
    """Token 存储管理器"""

    TOKEN_FILE = Path.home() / ".claude-backup" / "token.enc"
    USER_FILE = Path.home() / ".claude-backup" / "user.json"

    def __init__(self, crypto: Crypto = None):
        """初始化 Token 管理器

        Args:
            crypto: 加密工具实例，如果不提供则自动创建
        """
        self.crypto = crypto or Crypto()
        self._ensure_directories()

    def _ensure_directories(self):
        """确保存储目录存在"""
        self.TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.USER_FILE.parent.mkdir(parents=True, exist_ok=True)

    def save_token(self, token: str) -> None:
        """加密并保存 Token

        Args:
            token: 访问令牌
        """
        encrypted = self.crypto.encrypt(token)
        self.TOKEN_FILE.write_text(encrypted, encoding="utf-8")
        logger.info("Token saved successfully")

    def load_token(self) -> Optional[str]:
        """加载并解密 Token

        Returns:
            解密后的 Token，如果不存在则返回 None
        """
        if not self.TOKEN_FILE.exists():
            logger.debug("Token file does not exist")
            return None

        try:
            encrypted = self.TOKEN_FILE.read_text(encoding="utf-8")
            token = self.crypto.decrypt(encrypted)
            logger.info("Token loaded successfully")
            return token
        except Exception as e:
            logger.error(f"Failed to load token: {e}")
            return None

    def clear_token(self) -> None:
        """删除存储的 Token"""
        if self.TOKEN_FILE.exists():
            self.TOKEN_FILE.unlink()
            logger.info("Token cleared")

    def save_user_info(self, user_info: Dict[str, Any]) -> None:
        """保存用户信息到 JSON 文件

        Args:
            user_info: 用户信息字典
        """
        with open(self.USER_FILE, "w", encoding="utf-8") as f:
            json.dump(user_info, f, ensure_ascii=False, indent=2)
        logger.info(f"User info saved for: {user_info.get('login')}")

    def load_user_info(self) -> Optional[Dict[str, Any]]:
        """加载用户信息

        Returns:
            用户信息字典，如果不存在则返回 None
        """
        if not self.USER_FILE.exists():
            logger.debug("User info file does not exist")
            return None

        try:
            with open(self.USER_FILE, "r", encoding="utf-8") as f:
                user_info = json.load(f)
            logger.info(f"User info loaded for: {user_info.get('login')}")
            return user_info
        except Exception as e:
            logger.error(f"Failed to load user info: {e}")
            return None

    def is_logged_in(self) -> bool:
        """检查是否已登录

        Returns:
            如果存在有效的 Token 则返回 True
        """
        token = self.load_token()
        return token is not None and len(token) > 0