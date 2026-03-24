# tests/test_mysql_client.py
import pytest
import sys
sys.path.insert(0, 'src')

from unittest.mock import patch, MagicMock
from database.mysql_client import MySQLClient


class TestMySQLClient:
    def test_connection_params(self):
        """测试连接参数"""
        client = MySQLClient(
            host="localhost",
            port=3306,
            user="root",
            password="test",
            database="test_db"
        )
        assert client.host == "localhost"
        assert client.port == 3306

    @patch('pymysql.connect')
    def test_connect(self, mock_connect):
        """测试连接"""
        mock_connect.return_value = MagicMock()
        client = MySQLClient(
            host="localhost",
            port=3306,
            user="root",
            password="test",
            database="test_db"
        )
        client.connect()
        mock_connect.assert_called_once()
        assert client.is_connected

    @patch('pymysql.connect')
    def test_execute_query(self, mock_connect):
        """测试执行查询"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        client = MySQLClient(
            host="localhost",
            port=3306,
            user="root",
            password="test",
            database="test_db"
        )
        client.connect()
        result = client.execute("SELECT * FROM users")

        assert len(result) == 1
        assert result[0]["name"] == "test"