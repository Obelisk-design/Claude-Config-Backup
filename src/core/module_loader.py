# -*- coding: utf-8 -*-
"""备份模块加载器"""

import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

from utils.logger import logger


def get_config_dir():
    """获取配置目录，兼容开发环境和打包环境"""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / "config"
    else:
        return Path(__file__).parent.parent.parent / "config"


# 配置目录
CONFIG_DIR = get_config_dir()
# Claude 配置目录
CLAUDE_DIR = Path.home() / ".claude"


class ModuleLoader:
    """备份模块加载器"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or str(CONFIG_DIR / "modules.yaml")
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
                logger.debug(f"加载模块配置: {len(config.get('modules', {}))} 个模块")
                return config
        except FileNotFoundError:
            logger.warning(f"模块配置文件不存在: {self.config_path}")
            return {"modules": {}, "premium_modules": {}}

    def get_all_modules(self) -> List[Dict[str, Any]]:
        """获取所有模块"""
        modules = []

        # 内置模块
        for module_id, module_config in self.config.get("modules", {}).items():
            module_config["id"] = module_id
            modules.append(module_config)

        # 付费模块
        for module_id, module_config in self.config.get("premium_modules", {}).items():
            module_config["id"] = module_id
            modules.append(module_config)

        return modules

    def get_enabled_modules(self) -> List[Dict[str, Any]]:
        """获取启用的模块"""
        return [m for m in self.get_all_modules() if m.get("enabled", True)]

    def get_free_modules(self) -> List[Dict[str, Any]]:
        """获取免费模块"""
        return [m for m in self.get_enabled_modules() if not m.get("is_premium", False)]

    def get_module_by_id(self, module_id: str) -> Optional[Dict[str, Any]]:
        """根据 ID 获取模块"""
        for m in self.get_all_modules():
            if m["id"] == module_id:
                return m
        return None

    def resolve_paths(self, module: Dict) -> List[Path]:
        """解析模块的实际文件路径"""
        paths = []
        exclude_patterns = module.get("exclude", [])

        for path_config in module.get("paths", []):
            pattern = path_config["pattern"]

            if "**" in pattern:
                # glob 模式
                matched = list(CLAUDE_DIR.glob(pattern))
                for p in matched:
                    if self._should_include(p, exclude_patterns):
                        paths.append(p)
            else:
                # 单个文件
                full_path = CLAUDE_DIR / pattern
                if full_path.exists() and self._should_include(full_path, exclude_patterns):
                    paths.append(full_path)

        return [p for p in paths if p.is_file()]

    def _should_include(self, path: Path, exclude_patterns: List[str]) -> bool:
        """检查路径是否应该被包含"""
        path_str = str(path)
        for pattern in exclude_patterns:
            if pattern.startswith("*"):
                if path_str.endswith(pattern[1:]):
                    return False
            elif pattern in path_str:
                return False
        return True

    def get_module_size(self, module: Dict) -> int:
        """获取模块总大小（字节）"""
        total = 0
        for path in self.resolve_paths(module):
            try:
                total += path.stat().st_size
            except:
                pass
        return total