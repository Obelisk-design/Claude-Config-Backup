# tests/test_sensitive_filter.py
import pytest
import sys
sys.path.insert(0, 'src')

from security.sensitive_filter import SensitiveFilter


class TestSensitiveFilter:
    def test_mask_token(self):
        """测试 Token 脱敏"""
        filter = SensitiveFilter()
        data = {
            "API_TOKEN": "secret123",
            "normal_field": "value"
        }
        result = filter.filter(data)

        assert result["API_TOKEN"] == "***MASKED***"
        assert result["normal_field"] == "value"

    def test_exclude_token(self):
        """测试排除字段"""
        filter = SensitiveFilter()
        data = {
            "ANTHROPIC_AUTH_TOKEN": "sk-xxx",
            "other": "value"
        }
        result = filter.filter(data)

        assert "ANTHROPIC_AUTH_TOKEN" not in result
        assert result["other"] == "value"

    def test_nested_data(self):
        """测试嵌套数据"""
        filter = SensitiveFilter()
        data = {
            "env": {
                "DB_PASSWORD": "pass123",
                "DB_HOST": "localhost"
            }
        }
        result = filter.filter(data)

        assert result["env"]["DB_PASSWORD"] == "***MASKED***"
        assert result["env"]["DB_HOST"] == "localhost"

    def test_has_sensitive(self):
        """测试检测敏感信息"""
        filter = SensitiveFilter()

        assert filter.has_sensitive({"API_TOKEN": "xxx"}) is True
        assert filter.has_sensitive({"normal": "value"}) is False

    def test_get_sensitive_keys(self):
        """测试获取敏感字段路径"""
        filter = SensitiveFilter()
        data = {
            "API_TOKEN": "xxx",
            "env": {
                "DB_PASSWORD": "pass"
            }
        }
        keys = filter.get_sensitive_keys(data)

        assert "API_TOKEN" in keys
        assert "env.DB_PASSWORD" in keys