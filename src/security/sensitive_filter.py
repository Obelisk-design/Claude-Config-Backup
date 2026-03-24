# -*- coding: utf-8 -*-
"""敏感信息过滤器"""

import yaml
import fnmatch
from pathlib import Path
from typing import Dict, Any, List, Optional

from utils.logger import logger

# 配置目录
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"


class SensitiveFilter:
    """敏感信息过滤器"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or str(CONFIG_DIR / "sensitive_fields.yaml")
        self.patterns = []
        self.mask_value = "***MASKED***"
        self._load_config()

    def _load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
                self.patterns = config.get("patterns", [])
                self.mask_value = config.get("mask_value", "***MASKED***")
                logger.debug(f"加载敏感字段配置: {len(self.patterns)} 个规则")
        except FileNotFoundError:
            # 默认规则
            self.patterns = [
                {"pattern": "*_TOKEN", "action": "mask"},
                {"pattern": "*_PASSWORD", "action": "mask"},
                {"pattern": "*_SECRET", "action": "mask"},
            ]

    def _match_pattern(self, key: str, pattern: str) -> bool:
        """检查 key 是否匹配模式"""
        return fnmatch.fnmatch(key.upper(), pattern.upper())

    def _get_action(self, key: str) -> Optional[str]:
        """获取字段的处理动作"""
        for rule in self.patterns:
            if self._match_pattern(key, rule["pattern"]):
                return rule.get("action", "mask")
        return None

    def filter(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """过滤敏感信息"""
        result = {}
        for key, value in data.items():
            action = self._get_action(key)

            if action == "exclude":
                continue
            elif action == "mask":
                if isinstance(value, dict):
                    result[key] = self.filter(value)
                else:
                    result[key] = self.mask_value
            else:
                if isinstance(value, dict):
                    result[key] = self.filter(value)
                else:
                    result[key] = value

        return result

    def has_sensitive(self, data: Dict[str, Any]) -> bool:
        """检查数据是否包含敏感信息"""
        for key, value in data.items():
            if self._get_action(key):
                return True
            if isinstance(value, dict) and self.has_sensitive(value):
                return True
        return False

    def get_sensitive_keys(self, data: Dict[str, Any], prefix: str = "") -> List[str]:
        """获取所有敏感字段的路径"""
        keys = []
        for key, value in data.items():
            path = f"{prefix}.{key}" if prefix else key
            if self._get_action(key):
                keys.append(path)
            if isinstance(value, dict):
                keys.extend(self.get_sensitive_keys(value, path))
        return keys