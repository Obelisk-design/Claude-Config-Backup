# -*- coding: utf-8 -*-
"""MySQL 客户端"""

import pymysql
from pymysql.cursors import DictCursor
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from utils.logger import logger
from core.exceptions import NetworkError


class MySQLClient:
    """MySQL 数据库客户端"""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        charset: str = "utf8mb4",
        connect_timeout: int = 10
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.connect_timeout = connect_timeout

        self._connection: Optional[pymysql.Connection] = None

    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        if self._connection is None:
            return False
        try:
            self._connection.ping(reconnect=True)
            return True
        except:
            return False

    def connect(self):
        """建立连接"""
        try:
            self._connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset,
                cursorclass=DictCursor,
                connect_timeout=self.connect_timeout
            )
            logger.info(f"MySQL 连接成功: {self.host}:{self.port}/{self.database}")
        except pymysql.Error as e:
            logger.error(f"MySQL 连接失败: {e}")
            raise NetworkError(f"数据库连接失败: {e}")

    def disconnect(self):
        """断开连接"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("MySQL 连接已断开")

    @contextmanager
    def cursor(self):
        """获取游标上下文管理器"""
        if not self.is_connected:
            self.connect()

        cursor = self._connection.cursor()
        try:
            yield cursor
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            logger.error(f"SQL 执行错误: {e}")
            raise
        finally:
            cursor.close()

    def execute(
        self,
        sql: str,
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """执行 SQL 查询"""
        with self.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def execute_one(
        self,
        sql: str,
        params: Optional[tuple] = None
    ) -> Optional[Dict[str, Any]]:
        """执行 SQL 查询并返回单条结果"""
        with self.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """插入数据"""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        with self.cursor() as cursor:
            cursor.execute(sql, tuple(data.values()))
            return cursor.lastrowid

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: str,
        where_params: Optional[tuple] = None
    ) -> int:
        """更新数据"""
        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"

        with self.cursor() as cursor:
            cursor.execute(sql, tuple(data.values()) + (where_params or ()))
            return cursor.rowcount