# -*- coding: utf-8 -*-
"""配置管理"""

import yaml
import json
from pathlib import Path
from typing import Any, Dict, Optional

# 配置路径
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
USER_CONFIG_DIR = Path.home() / ".claude-backup"
USER_CONFIG_FILE = USER_CONFIG_DIR / "config.json"


class Config:
    """配置管理器"""

    _instance: Optional['Config'] = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """加载配置"""
        # 加载默认配置
        default_config_path = CONFIG_DIR / "settings.yaml"
        if default_config_path.exists():
            with open(default_config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}

        # 加载用户配置（覆盖默认）
        if USER_CONFIG_FILE.exists():
            with open(USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                self._deep_merge(self._config, user_config)

    def _deep_merge(self, base: Dict, override: Dict):
        """深度合并字典"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点分隔的嵌套键"""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self):
        """保存用户配置"""
        USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(USER_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def reload(self):
        """重新加载配置"""
        self._load_config()


def get_config() -> Config:
    """获取配置单例"""
    return Config()