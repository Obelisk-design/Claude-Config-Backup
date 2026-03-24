# -*- coding: utf-8 -*-
"""SQLite 离线缓存"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from utils.logger import logger

# 默认缓存路径
DEFAULT_CACHE_PATH = Path.home() / ".claude-backup" / "cache.db"


class SQLiteCache:
    """SQLite 本地缓存"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DEFAULT_CACHE_PATH)
        self._conn: Optional[sqlite3.Connection] = None
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self):
        """关闭数据库连接"""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def _init_database(self):
        """初始化数据库表"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = self._get_connection()
        cursor = conn.cursor()

        # 用户缓存表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                github_id TEXT UNIQUE NOT NULL,
                github_login TEXT NOT NULL,
                github_avatar TEXT,
                github_email TEXT,
                user_type TEXT DEFAULT 'free',
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dirty INTEGER DEFAULT 0
            )
        """)

        # 备份记录缓存表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_id TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                storage_type TEXT,
                storage_path TEXT,
                file_size INTEGER,
                file_hash TEXT,
                description TEXT,
                modules TEXT,
                status TEXT DEFAULT 'pending',
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dirty INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 待同步队列
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_sync (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                table_name TEXT NOT NULL,
                record_id INTEGER NOT NULL,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        logger.debug(f"SQLite 缓存数据库初始化完成: {self.db_path}")

    def save_user(self, user_data: Dict[str, Any]) -> int:
        """保存用户缓存"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO users
            (github_id, github_login, github_avatar, github_email, user_type, dirty)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (
            user_data.get("github_id"),
            user_data.get("github_login"),
            user_data.get("github_avatar"),
            user_data.get("github_email"),
            user_data.get("user_type", "free")
        ))

        conn.commit()
        return cursor.lastrowid

    def get_user(self, github_id: str) -> Optional[Dict[str, Any]]:
        """获取用户缓存"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE github_id = ?",
            (github_id,)
        )
        row = cursor.fetchone()

        return dict(row) if row else None

    def save_backup(self, backup_data: Dict[str, Any]) -> int:
        """保存备份记录缓存"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO backups
            (backup_id, user_id, storage_type, storage_path, file_size,
             file_hash, description, modules, status, dirty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            backup_data.get("backup_id"),
            backup_data.get("user_id"),
            backup_data.get("storage_type"),
            backup_data.get("storage_path"),
            backup_data.get("file_size"),
            backup_data.get("file_hash"),
            backup_data.get("description"),
            json.dumps(backup_data.get("modules", [])),
            backup_data.get("status", "pending")
        ))

        conn.commit()
        return cursor.lastrowid

    def get_backups(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """获取用户的备份列表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM backups
            WHERE user_id = ?
            ORDER BY cached_at DESC
            LIMIT ?
        """, (user_id, limit))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_pending_sync(self) -> List[Dict[str, Any]]:
        """获取待同步队列"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pending_sync ORDER BY created_at")
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def clear_pending_sync(self, record_ids: List[int]):
        """清除已同步的记录"""
        if not record_ids:
            return

        conn = self._get_connection()
        cursor = conn.cursor()
        placeholders = ", ".join("?" * len(record_ids))
        cursor.execute(
            f"DELETE FROM pending_sync WHERE id IN ({placeholders})",
            record_ids
        )
        conn.commit()