# utils/logger.py
"""
日志层：标准库 logging 配置，控制台 + 文件双输出。

特性：
1. 彩色控制台输出（Windows 也兼容）
2. 按日期滚动文件日志，存到 logs/ 目录
3. pytest-xdist 并发下每个 worker 独立日志文件
4. 关键操作自动 attach 到 Allure 报告

用法：
    from utils.logger import get_logger
    log = get_logger(__name__)
    log.info("开始登录")
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

from config.settings import settings

_LOGGER_CACHE: dict[str, logging.Logger] = {}
_INITIALIZED = False


def _init_root_logger() -> None:
    """初始化根日志器（只执行一次）"""
    global _INITIALIZED
    if _INITIALIZED:
        return
    _INITIALIZED = True

    # 确保日志目录存在
    settings.log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # 根级全收，由 handler 决定输出级别

    # 避免重复添加 handler（pytest 多次 import 时）
    if root.handlers:
        return

    # ---------- 控制台 handler ----------
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(settings.log_level)
    console.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    root.addHandler(console)

    # ---------- 文件 handler（按日期 + worker id 滚动）----------
    worker_id = _get_xdist_worker_id()
    log_filename = f"test_{datetime.now().strftime('%Y%m%d')}"
    if worker_id:
        log_filename += f"_{worker_id}"
    log_filename += ".log"

    file_handler = logging.FileHandler(
        settings.log_dir / log_filename,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)  # 文件保留全部级别
    file_handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(file_handler)


def _get_xdist_worker_id() -> str:
    """获取 pytest-xdist worker id（gw0/gw1/...），非并发时为空"""
    import os
    return os.environ.get("PYTEST_XDIST_WORKER", "")


def get_logger(name: str = "test") -> logging.Logger:
    """获取/创建 logger。

    Args:
        name: 通常传 __name__，或模块名/业务名

    Returns:
        logging.Logger 实例
    """
    if not _INITIALIZED:
        _init_root_logger()

    if name in _LOGGER_CACHE:
        return _LOGGER_CACHE[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    _LOGGER_CACHE[name] = logger
    return logger


def log_to_allure(message: str, level: str = "INFO") -> None:
    """把日志条目附加到 Allure 报告（如果可用）"""
    try:
        import allure
        allure.attach(message, name="log", attachment_type=allure.attachment_type.TEXT)
    except Exception:
        # allure 不可用时静默降级
        pass
