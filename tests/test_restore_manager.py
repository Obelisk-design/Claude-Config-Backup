# tests/test_restore_manager.py
import pytest
import sys
import os
import json
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime

sys.path.insert(0, 'src')

from core.restore_manager import RestoreManager
from core.exceptions import RestoreError, CorruptedFileError, VersionMismatchError


class TestRestoreManager:
    """RestoreManager 测试类"""

    @pytest.fixture
    def temp_dirs(self, tmp_path):
        """创建临时目录"""
        claude_dir = tmp_path / "claude"
        cache_dir = tmp_path / "cache"
        rollback_dir = tmp_path / "rollback"

        claude_dir.mkdir()
        cache_dir.mkdir()
        rollback_dir.mkdir()

        return {
            "claude_dir": claude_dir,
            "cache_dir": cache_dir,
            "rollback_dir": rollback_dir
        }

    @pytest.fixture
    def valid_backup(self, tmp_path):
        """创建有效的测试备份文件"""
        backup_path = tmp_path / "test_backup.ccb"

        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 添加 manifest.json
            manifest = {
                "version": "1.0",
                "app_version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "username": "test_user",
                "description": "Test backup",
                "modules": [
                    {"name": "core", "files": 2, "size": 1024}
                ],
                "total_files": 2,
                "total_size": 1024,
                "platform": "windows",
                "claude_version": "2.1.81"
            }
            zf.writestr('manifest.json', json.dumps(manifest, indent=2))

            # 添加 snapshot.json
            snapshot = {
                "backup_id": "20260324_153000",
                "modules": {
                    "core": {
                        "files": [
                            {"path": "settings.json", "size": 100, "hash": "sha256:abc123"}
                        ]
                    }
                }
            }
            zf.writestr('snapshot.json', json.dumps(snapshot, indent=2))

            # 添加 checksum.json
            checksum = {
                "algorithm": "sha256",
                "files": {
                    "data/core/settings.json": "abc123def456",
                    "data/core/config.json": "789xyz012"
                }
            }
            zf.writestr('checksum.json', json.dumps(checksum, indent=2))

            # 添加数据文件
            settings_content = {"test_key": "test_value"}
            zf.writestr('data/core/settings.json', json.dumps(settings_content))

            config_content = {"api_key": "test_api_key"}
            zf.writestr('data/core/config.json', json.dumps(config_content))

        return backup_path

    @pytest.fixture
    def invalid_backup_no_manifest(self, tmp_path):
        """创建缺少 manifest 的无效备份文件"""
        backup_path = tmp_path / "invalid_backup.ccb"

        with zipfile.ZipFile(backup_path, 'w') as zf:
            # 只有 checksum.json，缺少 manifest.json
            checksum = {"algorithm": "sha256", "files": {}}
            zf.writestr('checksum.json', json.dumps(checksum))

        return backup_path

    @pytest.fixture
    def invalid_backup_bad_zip(self, tmp_path):
        """创建损坏的 ZIP 文件"""
        backup_path = tmp_path / "corrupted.ccb"
        with open(backup_path, 'wb') as f:
            f.write(b'Not a valid zip file content')
        return backup_path

    @pytest.fixture
    def invalid_backup_bad_version(self, tmp_path):
        """创建版本不兼容的备份文件"""
        backup_path = tmp_path / "bad_version.ccb"

        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 版本号不兼容
            manifest = {
                "version": "2.0",  # 不支持的版本
                "app_version": "1.0.0",
                "created_at": datetime.now().isoformat(),
            }
            zf.writestr('manifest.json', json.dumps(manifest, indent=2))

            checksum = {"algorithm": "sha256", "files": {}}
            zf.writestr('checksum.json', json.dumps(checksum, indent=2))

        return backup_path

    def test_validate_backup_valid(self, temp_dirs, valid_backup):
        """测试验证有效的备份文件"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        result = manager.validate_backup(valid_backup)
        assert result is True

    def test_validate_backup_not_found(self, temp_dirs):
        """测试验证不存在的备份文件"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        with pytest.raises(RestoreError) as exc_info:
            manager.validate_backup(Path("/non/existent/backup.ccb"))

        assert "not found" in str(exc_info.value).lower()

    def test_validate_backup_corrupted_zip(self, temp_dirs, invalid_backup_bad_zip):
        """测试验证损坏的 ZIP 文件"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        with pytest.raises(CorruptedFileError):
            manager.validate_backup(invalid_backup_bad_zip)

    def test_validate_backup_missing_manifest(self, temp_dirs, invalid_backup_no_manifest):
        """测试验证缺少 manifest 的备份文件"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        with pytest.raises(CorruptedFileError):
            manager.validate_backup(invalid_backup_no_manifest)

    def test_validate_backup_version_mismatch(self, temp_dirs, invalid_backup_bad_version):
        """测试验证版本不兼容的备份文件"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        with pytest.raises(VersionMismatchError):
            manager.validate_backup(invalid_backup_bad_version)

    def test_extract_manifest_success(self, temp_dirs, valid_backup):
        """测试成功提取 manifest"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        manifest = manager.extract_manifest(valid_backup)

        assert manifest is not None
        assert manifest["version"] == "1.0"
        assert manifest["username"] == "test_user"
        assert "modules" in manifest

    def test_extract_manifest_not_found(self, temp_dirs):
        """测试提取不存在文件的 manifest"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        with pytest.raises(RestoreError):
            manager.extract_manifest(Path("/non/existent/backup.ccb"))

    def test_extract_manifest_missing_in_zip(self, temp_dirs, invalid_backup_no_manifest):
        """测试提取缺少 manifest 的备份文件"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        with pytest.raises(CorruptedFileError):
            manager.extract_manifest(invalid_backup_no_manifest)

    def test_create_rollback(self, temp_dirs):
        """测试创建回滚点"""
        # 在 claude_dir 中创建一些测试文件
        claude_dir = temp_dirs["claude_dir"]
        (claude_dir / "settings.json").write_text('{"test": "value"}')
        (claude_dir / "config.json").write_text('{"config": "data"}')

        skills_dir = claude_dir / "skills"
        skills_dir.mkdir()
        (skills_dir / "test_skill.md").write_text("# Test Skill")

        manager = RestoreManager(
            claude_dir=claude_dir,
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        rollback_id = manager.create_rollback()

        assert rollback_id is not None

        # 检查回滚目录是否创建
        rollback_path = temp_dirs["rollback_dir"] / rollback_id
        assert rollback_path.exists()

        # 检查文件是否被复制
        assert (rollback_path / "settings.json").exists()
        assert (rollback_path / "config.json").exists()
        assert (rollback_path / "skills" / "test_skill.md").exists()

        # 检查元数据文件
        assert (rollback_path / ".rollback_meta.json").exists()

    def test_create_rollback_empty_dir(self, temp_dirs):
        """测试空目录创建回滚点"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        rollback_id = manager.create_rollback("test_rollback")

        assert rollback_id == "test_rollback"
        rollback_path = temp_dirs["rollback_dir"] / "test_rollback"
        assert rollback_path.exists()

    def test_create_rollback_nonexistent_claude_dir(self, tmp_path):
        """测试 Claude 目录不存在时创建回滚点"""
        manager = RestoreManager(
            claude_dir=tmp_path / "nonexistent",
            cache_dir=tmp_path / "cache",
            rollback_dir=tmp_path / "rollback"
        )

        rollback_id = manager.create_rollback()

        # Claude 目录不存在时应返回 None
        assert rollback_id is None

    def test_list_rollback_points(self, temp_dirs):
        """测试列出回滚点"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        # 创建多个回滚点
        manager.create_rollback("rollback_1")
        manager.create_rollback("rollback_2")
        manager.create_rollback("rollback_3")

        rollback_points = manager.list_rollback_points()

        assert len(rollback_points) == 3
        rollback_ids = [rp["id"] for rp in rollback_points]
        assert "rollback_1" in rollback_ids
        assert "rollback_2" in rollback_ids
        assert "rollback_3" in rollback_ids

    def test_list_rollback_points_empty(self, temp_dirs):
        """测试空回滚目录"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        rollback_points = manager.list_rollback_points()

        assert len(rollback_points) == 0

    def test_restore_success(self, temp_dirs, valid_backup):
        """测试成功恢复"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        result = manager.restore(valid_backup, create_rollback=False)

        assert result["success"] is True
        assert len(result["restored_files"]) > 0
        assert len(result["errors"]) == 0

        # 检查文件是否恢复
        settings_path = temp_dirs["claude_dir"] / "settings.json"
        assert settings_path.exists()

        config_path = temp_dirs["claude_dir"] / "config.json"
        assert config_path.exists()

        # 检查文件内容
        settings = json.loads(settings_path.read_text())
        assert settings["test_key"] == "test_value"

    def test_restore_with_rollback(self, temp_dirs, valid_backup):
        """测试带回滚点的恢复"""
        # 创建一个已存在的文件
        existing_file = temp_dirs["claude_dir"] / "settings.json"
        existing_file.write_text('{"existing": "data"}')

        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        result = manager.restore(valid_backup, create_rollback=True)

        assert result["success"] is True
        assert result["rollback_id"] is not None

        # 检查回滚点是否创建
        rollback_points = manager.list_rollback_points()
        assert len(rollback_points) == 1

    def test_restore_skip_existing(self, temp_dirs, valid_backup):
        """测试跳过已存在文件"""
        # 创建已存在的文件
        existing_file = temp_dirs["claude_dir"] / "settings.json"
        existing_file.write_text('{"existing": "data"}')

        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        result = manager.restore(valid_backup, skip_existing=True, create_rollback=False)

        assert result["success"] is True
        assert "settings.json" in result["skipped_files"]

        # 确认文件没有被覆盖
        content = json.loads(existing_file.read_text())
        assert content["existing"] == "data"

    def test_restore_specific_modules(self, temp_dirs, tmp_path):
        """测试恢复特定模块"""
        # 创建包含多个模块的备份
        backup_path = tmp_path / "multi_module.ccb"

        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            manifest = {
                "version": "1.0",
                "app_version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "username": "test_user",
                "modules": [
                    {"name": "core", "files": 1, "size": 100},
                    {"name": "skills", "files": 1, "size": 200}
                ]
            }
            zf.writestr('manifest.json', json.dumps(manifest, indent=2))
            zf.writestr('checksum.json', json.dumps({"algorithm": "sha256", "files": {}}))
            zf.writestr('data/core/settings.json', json.dumps({"from_core": True}))
            zf.writestr('data/skills/test.md', "# Test Skill")

        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        result = manager.restore(backup_path, modules=["core"], create_rollback=False)

        assert result["success"] is True

        # core 文件应该被恢复
        assert (temp_dirs["claude_dir"] / "settings.json").exists()

        # skills 文件不应该被恢复
        assert not (temp_dirs["claude_dir"] / "test.md").exists()

    def test_restore_invalid_backup(self, temp_dirs, invalid_backup_bad_zip):
        """测试恢复无效备份"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        result = manager.restore(invalid_backup_bad_zip, create_rollback=False)

        assert result["success"] is False
        assert len(result["errors"]) > 0

    def test_restore_nonexistent_file(self, temp_dirs):
        """测试恢复不存在的文件"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        result = manager.restore(Path("/non/existent/backup.ccb"), create_rollback=False)

        assert result["success"] is False
        assert len(result["errors"]) > 0

    def test_delete_rollback_point(self, temp_dirs):
        """测试删除回滚点"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        # 创建回滚点
        rollback_id = manager.create_rollback("test_delete")

        # 确认回滚点存在
        rollback_path = temp_dirs["rollback_dir"] / rollback_id
        assert rollback_path.exists()

        # 删除回滚点
        result = manager.delete_rollback_point(rollback_id)

        assert result is True
        assert not rollback_path.exists()

    def test_delete_nonexistent_rollback_point(self, temp_dirs):
        """测试删除不存在的回滚点"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        result = manager.delete_rollback_point("nonexistent")

        assert result is False

    def test_manager_initialization_default_paths(self):
        """测试默认路径初始化"""
        manager = RestoreManager()

        # 验证默认路径
        assert manager.claude_dir == Path.home() / ".claude"
        assert manager.cache_dir == Path.home() / ".claude-backup" / "cache"
        assert manager.rollback_dir == Path.home() / ".claude-backup" / "rollback"

    def test_manager_initialization_custom_paths(self, temp_dirs):
        """测试自定义路径初始化"""
        manager = RestoreManager(
            claude_dir=temp_dirs["claude_dir"],
            cache_dir=temp_dirs["cache_dir"],
            rollback_dir=temp_dirs["rollback_dir"]
        )

        assert manager.claude_dir == temp_dirs["claude_dir"]
        assert manager.cache_dir == temp_dirs["cache_dir"]
        assert manager.rollback_dir == temp_dirs["rollback_dir"]