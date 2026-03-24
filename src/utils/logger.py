# -*- coding: utf-8 -*-
"""日志工具"""

import logging
import sys
from pathlib import Path
from typing import Optional

# 日志目录
LOG_DIR = Path.home() / ".claude-backup" / "logs"


def setup_logger(
    name: str = "claude-backup",
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """设置日志器

    Args:
        name: 日志器名称
        level: 日志级别
        log_file: 日志文件名（不含路径）

    Returns:
        配置好的日志器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # 文件输出
    if log_file:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_path = LOG_DIR / log_file
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(level)
        file_format = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(module)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


# 默认日志器
logger = setup_logger(log_file="app.log")