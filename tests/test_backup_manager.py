# tests/test_backup_manager.py
import pytest
import sys
import os
import json
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

sys.path.insert(0, 'src')

from core.backup_manager import BackupManager, CACHE_DIR, CLAUDE_DIR
from core.exceptions import BackupError


class TestBackupManager:
    """备份管理器测试"""

    def test_generate_backup_id(self):
        """测试备份ID生成"""
        manager = BackupManager()
        backup_id = manager._generate_backup_id()

        # 验证格式：YYYYMMDD_HHMMSS
        assert len(backup_id) == 15
        assert backup_id[8] == "_"

        # 验证可以解析为日期时间
        date_part = backup_id[:8]
        time_part = backup_id[9:]
        assert date_part.isdigit()
        assert time_part.isdigit()

        # 验证日期有效性
        year = int(date_part[:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        assert 2020 <= year <= 2100
        assert 1 <= month <= 12
        assert 1 <= day <= 31

        # 验证时间有效性
        hour = int(time_part[:2])
        minute = int(time_part[2:4])
        second = int(time_part[4:6])
        assert 0 <= hour <= 23
        assert 0 <= minute <= 59
        assert 0 <= second <= 59

    def test_create_manifest(self):
        """测试创建清单文件"""
        manager = BackupManager()
        backup_id = "20240101_120000"
        manifest = manager._create_manifest(
            backup_id=backup_id,
            username="test_user",
            description="Test backup",
            modules=["core", "skills"],
            total_files=10,
            total_size=1024
        )

        assert manifest["version"] == "1.0"
        assert manifest["app_version"] == manager.app_version
        assert manifest["backup_id"] == backup_id
        assert manifest["username"] == "test_user"
        assert manifest["description"] == "Test backup"
        assert manifest["modules"] == ["core", "skills"]
        assert manifest["total_files"] == 10
        assert manifest["total_size"] == 1024
        assert "created_at" in manifest
        assert "platform" in manifest

    def test_create_snapshot(self):
        """测试创建快照文件"""
        manager = BackupManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试文件
            test_file = Path(tmpdir) / "test.json"
            test_file.write_text('{"key": "value"}', encoding="utf-8")

            files_by_module = {
                "core": [
                    {
                        "path": "test.json",
                        "full_path": str(test_file),
                        "size": 16,
                        "mtime": 1234567890,
                    }
                ]
            }

            snapshot = manager._create_snapshot("20240101_120000", files_by_module)

            assert snapshot["backup_id"] == "20240101_120000"
            assert "core" in snapshot["modules"]
            assert snapshot["modules"]["core"]["count"] == 1
            assert len(snapshot["modules"]["core"]["files"]) == 1

            file_info = snapshot["modules"]["core"]["files"][0]
            assert file_info["path"] == "test.json"
            assert file_info["size"] == 16
            assert "hash" in file_info
            assert file_info["mtime"] == 1234567890

    def test_create_checksum(self):
        """测试创建校验文件"""
        manager = BackupManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试文件
            test_file = Path(tmpdir) / "test.json"
            test_file.write_text('{"key": "value"}', encoding="utf-8")

            files_by_module = {
                "core": [
                    {
                        "path": "test.json",
                        "full_path": str(test_file),
                        "size": 16,
                        "mtime": 1234567890,
                    }
                ]
            }

            checksums = manager._create_checksum(files_by_module)

            assert "data/core/test.json" in checksums
            assert len(checksums["data/core/test.json"]) == 64  # SHA256 hex length

    def test_calculate_file_hash(self):
        """测试文件哈希计算"""
        manager = BackupManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("hello world", encoding="utf-8")

            file_hash = manager._calculate_file_hash(test_file)

            # SHA256 of "hello world"
            expected_hash = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
            assert file_hash == expected_hash

    def test_get_preview(self):
        """测试获取备份预览"""
        manager = BackupManager()

        # 获取预览（使用真实模块配置）
        preview = manager.get_preview(["core"])

        assert "modules" in preview
        assert "total_files" in preview
        assert "total_size" in preview
        assert "total_size_mb" in preview

    def test_create_backup_no_files(self):
        """测试创建备份时没有文件"""
        manager = BackupManager()

        # 使用不存在的模块
        with patch.object(manager.module_loader, 'get_module_by_id', return_value=None):
            with pytest.raises(BackupError) as exc_info:
                manager.create_backup(["nonexistent_module"])

            assert "没有可备份的文件" in str(exc_info.value)

    def test_create_backup_with_temp_files(self):
        """测试创建备份文件（使用临时文件）"""
        manager = BackupManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建模拟的 CLAUDE_DIR 结构
            mock_claude_dir = Path(tmpdir) / ".claude"
            mock_claude_dir.mkdir()

            # 创建测试文件
            settings_file = mock_claude_dir / "settings.json"
            settings_file.write_text('{"theme": "dark"}', encoding="utf-8")

            # Mock CLAUDE_DIR
            with patch('core.backup_manager.CLAUDE_DIR', mock_claude_dir):
                # 重新创建 manager 以使用 mock 的路径
                manager = BackupManager()

                # Mock module_loader
                mock_module = {
                    "id": "core",
                    "name": "核心配置",
                    "paths": [{"pattern": "settings.json"}],
                    "exclude": [],
                }

                with patch.object(manager.module_loader, 'get_module_by_id', return_value=mock_module):
                    with patch.object(manager.module_loader, 'resolve_paths', return_value=[settings_file]):
                        # 创建备份
                        backup_id, backup_path = manager.create_backup(
                            module_ids=["core"],
                            description="Test backup",
                            username="test_user",
                            include_sensitive=True,
                            output_path=Path(tmpdir) / "test.ccb"
                        )

                        # 验证备份ID格式
                        assert len(backup_id) == 15
                        assert backup_id[8] == "_"

                        # 验证备份文件存在
                        assert backup_path.exists()

                        # 验证ZIP内容
                        with zipfile.ZipFile(backup_path, "r") as zf:
                            names = zf.namelist()
                            assert "manifest.json" in names
                            assert "snapshot.json" in names
                            assert "checksum.json" in names

                            # 验证manifest内容
                            manifest = json.loads(zf.read("manifest.json"))
                            assert manifest["version"] == "1.0"
                            assert manifest["username"] == "test_user"
                            assert manifest["description"] == "Test backup"
                            assert manifest["modules"] == ["core"]

                            # 验证snapshot内容
                            snapshot = json.loads(zf.read("snapshot.json"))
                            assert snapshot["backup_id"] == backup_id
                            assert "core" in snapshot["modules"]

    def test_filter_sensitive_content_json(self):
        """测试敏感信息过滤（JSON文件）"""
        manager = BackupManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "config.json"
            test_file.write_text('{"API_TOKEN": "secret123", "normal": "value"}', encoding="utf-8")

            filtered = manager._filter_sensitive_content(test_file)

            assert filtered is not None
            assert filtered.get("API_TOKEN") == "***MASKED***"
            assert filtered.get("normal") == "value"

    def test_filter_sensitive_content_non_json(self):
        """测试敏感信息过滤（非JSON文件）"""
        manager = BackupManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "readme.txt"
            test_file.write_text("This is plain text", encoding="utf-8")

            filtered = manager._filter_sensitive_content(test_file)

            # 非JSON文件应返回None
            assert filtered is None

    def test_backup_with_sensitive_filtering(self):
        """测试备份时过滤敏感信息"""
        manager = BackupManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_claude_dir = Path(tmpdir) / ".claude"
            mock_claude_dir.mkdir()

            # 创建包含敏感信息的JSON文件
            config_file = mock_claude_dir / "config.json"
            config_file.write_text(
                '{"API_TOKEN": "secret123", "normal_field": "value"}',
                encoding="utf-8"
            )

            with patch('core.backup_manager.CLAUDE_DIR', mock_claude_dir):
                manager = BackupManager()
                mock_module = {
                    "id": "core",
                    "name": "核心配置",
                    "paths": [{"pattern": "config.json"}],
                    "exclude": [],
                }

                with patch.object(manager.module_loader, 'get_module_by_id', return_value=mock_module):
                    with patch.object(manager.module_loader, 'resolve_paths', return_value=[config_file]):
                        backup_id, backup_path = manager.create_backup(
                            module_ids=["core"],
                            description="Filtered backup",
                            include_sensitive=False,
                            output_path=Path(tmpdir) / "filtered.ccb"
                        )

                        # 验证文件内容被过滤
                        with zipfile.ZipFile(backup_path, "r") as zf:
                            data_content = zf.read("data/core/config.json").decode("utf-8")
                            data = json.loads(data_content)

                            assert data.get("API_TOKEN") == "***MASKED***"
                            assert data.get("normal_field") == "value"


class TestBackupManagerIntegration:
    """集成测试"""

    def test_preview_and_backup_consistency(self):
        """测试预览和备份的一致性"""
        manager = BackupManager()

        # 如果实际配置目录存在文件，测试预览数据
        preview = manager.get_preview(["core", "skills"])

        # 验证预览结构
        assert isinstance(preview["modules"], list)
        assert isinstance(preview["total_files"], int)
        assert isinstance(preview["total_size"], int)
        assert isinstance(preview["total_size_mb"], float)

        # total_files 应该等于所有模块文件数之和
        expected_total = sum(m["files"] for m in preview["modules"])
        assert preview["total_files"] == expected_total

    def test_backup_file_structure(self):
        """测试备份文件结构完整性"""
        manager = BackupManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_claude_dir = Path(tmpdir) / ".claude"
            mock_claude_dir.mkdir()

            # 创建多个测试文件
            (mock_claude_dir / "settings.json").write_text('{"theme": "dark"}', encoding="utf-8")
            (mock_claude_dir / "config.json").write_text('{"lang": "zh"}', encoding="utf-8")

            with patch('core.backup_manager.CLAUDE_DIR', mock_claude_dir):
                manager = BackupManager()
                mock_module = {
                    "id": "core",
                    "name": "核心配置",
                    "paths": [
                        {"pattern": "settings.json"},
                        {"pattern": "config.json"}
                    ],
                    "exclude": [],
                }

                with patch.object(manager.module_loader, 'get_module_by_id', return_value=mock_module):
                    file_list = [
                        mock_claude_dir / "settings.json",
                        mock_claude_dir / "config.json"
                    ]
                    with patch.object(manager.module_loader, 'resolve_paths', return_value=file_list):
                        backup_id, backup_path = manager.create_backup(
                            module_ids=["core"],
                            description="Full structure test",
                            output_path=Path(tmpdir) / "structure.ccb"
                        )

                        with zipfile.ZipFile(backup_path, "r") as zf:
                            # 验证必需文件存在
                            assert "manifest.json" in zf.namelist()
                            assert "snapshot.json" in zf.namelist()
                            assert "checksum.json" in zf.namelist()

                            # 验证数据文件存在
                            assert "data/core/settings.json" in zf.namelist()
                            assert "data/core/config.json" in zf.namelist()

                            # 验证checksum包含所有数据文件
                            checksums = json.loads(zf.read("checksum.json"))
                            assert "data/core/settings.json" in checksums
                            assert "data/core/config.json" in checksums