# -*- coding: utf-8 -*-
"""加密工具"""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from utils.logger import logger


class Crypto:
    """AES-256 加密工具"""

    def __init__(self, key: str = None):
        """初始化

        Args:
            key: 加密密钥，如果不提供则从机器特征生成
        """
        if key:
            self.key = self._derive_key(key)
        else:
            self.key = self._generate_machine_key()

    def _derive_key(self, password: str) -> bytes:
        """从密码派生密钥"""
        return hashlib.sha256(password.encode()).digest()

    def _generate_machine_key(self) -> bytes:
        """从机器特征生成密钥"""
        import platform

        features = [
            platform.node(),
            platform.system(),
            os.path.expanduser("~"),
        ]

        combined = "|".join(features)
        return hashlib.sha256(combined.encode()).digest()

    def encrypt(self, plaintext: str) -> str:
        """加密字符串

        Args:
            plaintext: 明文

        Returns:
            Base64 编码的密文
        """
        iv = os.urandom(16)

        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        data = plaintext.encode('utf-8')
        padding_len = 16 - (len(data) % 16)
        padded_data = data + bytes([padding_len] * padding_len)

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        result = base64.b64encode(iv + ciphertext).decode('utf-8')
        return result

    def decrypt(self, ciphertext: str) -> str:
        """解密字符串

        Args:
            ciphertext: Base64 编码的密文

        Returns:
            明文
        """
        data = base64.b64decode(ciphertext.encode('utf-8'))

        iv = data[:16]
        actual_ciphertext = data[16:]

        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        padded_data = decryptor.update(actual_ciphertext) + decryptor.finalize()

        padding_len = padded_data[-1]
        plaintext = padded_data[:-padding_len].decode('utf-8')

        return plaintext