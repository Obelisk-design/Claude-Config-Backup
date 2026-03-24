# tests/test_crypto.py
import pytest
import sys
sys.path.insert(0, 'src')

from security.crypto import Crypto


class TestCrypto:
    def test_encrypt_decrypt(self):
        """测试加密解密"""
        crypto = Crypto()
        original = "my_secret_token"

        encrypted = crypto.encrypt(original)
        decrypted = crypto.decrypt(encrypted)

        assert decrypted == original
        assert encrypted != original

    def test_different_encryption(self):
        """测试相同内容不同加密结果"""
        crypto = Crypto()
        original = "same_content"

        encrypted1 = crypto.encrypt(original)
        encrypted2 = crypto.encrypt(original)

        assert encrypted1 != encrypted2
        assert crypto.decrypt(encrypted1) == original
        assert crypto.decrypt(encrypted2) == original

    def test_empty_string(self):
        """测试空字符串"""
        crypto = Crypto()
        original = ""

        encrypted = crypto.encrypt(original)
        decrypted = crypto.decrypt(encrypted)

        assert decrypted == original

    def test_long_string(self):
        """测试长字符串"""
        crypto = Crypto()
        original = "a" * 1000

        encrypted = crypto.encrypt(original)
        decrypted = crypto.decrypt(encrypted)

        assert decrypted == original

    def test_unicode(self):
        """测试 Unicode"""
        crypto = Crypto()
        original = "中文测试 🎉"

        encrypted = crypto.encrypt(original)
        decrypted = crypto.decrypt(encrypted)

        assert decrypted == original