# tests/test_module_loader.py
import pytest
import sys
sys.path.insert(0, 'src')

from core.module_loader import ModuleLoader


class TestModuleLoader:
    def test_load_config(self):
        """测试加载配置"""
        loader = ModuleLoader()
        assert loader.config is not None
        assert loader.config.get("version") == "1.0"

    def test_get_all_modules(self):
        """测试获取所有模块"""
        loader = ModuleLoader()
        modules = loader.get_all_modules()

        assert len(modules) >= 4
        module_ids = [m["id"] for m in modules]
        assert "core" in module_ids
        assert "skills" in module_ids

    def test_get_free_modules(self):
        """测试获取免费模块"""
        loader = ModuleLoader()
        modules = loader.get_free_modules()

        for m in modules:
            assert m.get("is_premium", False) is False

    def test_get_module_by_id(self):
        """测试根据 ID 获取模块"""
        loader = ModuleLoader()
        module = loader.get_module_by_id("core")

        assert module is not None
        assert module["name"] == "核心配置"

    def test_module_has_paths(self):
        """测试模块包含路径配置"""
        loader = ModuleLoader()
        module = loader.get_module_by_id("core")

        assert "paths" in module
        assert len(module["paths"]) > 0