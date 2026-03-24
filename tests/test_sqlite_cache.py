# tests/test_sqlite_cache.py
import pytest
import tempfile
import os
import sys
sys.path.insert(0, 'src')

from database.sqlite_cache import SQLiteCache


class TestSQLiteCache:
    def test_init_database(self):
        """测试初始化数据库"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            cache = SQLiteCache(db_path)
            assert os.path.exists(db_path)
            cache.close()

    def test_cache_user(self):
        """测试缓存用户"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            cache = SQLiteCache(db_path)

            user_data = {
                "github_id": "12345",
                "github_login": "testuser",
                "github_email": "test@example.com"
            }
            cache.save_user(user_data)

            user = cache.get_user("12345")
            assert user is not None
            assert user["github_login"] == "testuser"
            cache.close()

    def test_cache_backup(self):
        """测试缓存备份记录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            cache = SQLiteCache(db_path)

            backup_data = {
                "backup_id": "20260324_001",
                "user_id": 1,
                "storage_type": "github",
                "description": "test backup",
                "status": "completed"
            }
            cache.save_backup(backup_data)

            backups = cache.get_backups(user_id=1)
            assert len(backups) == 1
            assert backups[0]["backup_id"] == "20260324_001"
            cache.close()

    def test_get_pending_sync(self):
        """测试获取待同步队列"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            cache = SQLiteCache(db_path)

            pending = cache.get_pending_sync()
            assert isinstance(pending, list)
            cache.close()

    def test_context_manager(self):
        """测试上下文管理器"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            with SQLiteCache(db_path) as cache:
                user_data = {
                    "github_id": "67890",
                    "github_login": "contextuser",
                    "github_email": "context@example.com"
                }
                cache.save_user(user_data)
                user = cache.get_user("67890")
                assert user is not None
                assert user["github_login"] == "contextuser"