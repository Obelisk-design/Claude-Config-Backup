# tests/test_config.py
import pytest
import sys
sys.path.insert(0, 'src')

from utils.config import Config, get_config


class TestConfig:
    def test_load_default_config(self):
        """测试加载默认配置"""
        config = Config()
        assert config.get("app.name") == "Claude Config Backup"
        assert config.get("app.language") == "zh_CN"

    def test_get_nested_value(self):
        """测试获取嵌套值"""
        config = Config()
        assert config.get("database.host") == "43.153.156.249"
        assert config.get("database.port") == 3306

    def test_get_default_value(self):
        """测试获取默认值"""
        config = Config()
        assert config.get("nonexistent.key", "default") == "default"

    def test_set_value(self):
        """测试设置值"""
        config = Config()
        config.set("test.key", "value")
        assert config.get("test.key") == "value"

    def test_singleton(self):
        """测试单例模式"""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2