# config/settings.py
"""
配置层：集中管理环境、浏览器、超时、账号等运行参数。

设计原则：
1. 优先级：环境变量 > .env 文件 > 代码默认值
2. 不引入额外依赖（dataclass + os.environ + 自实现 .env 解析）
3. 全局单例 `settings`，任何模块 import 即可使用
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# 项目根目录（config/ 的上一级）
ROOT_DIR = Path(__file__).resolve().parent.parent


def _parse_bool(value: str | None, default: bool = False) -> bool:
    """容错解析布尔环境变量"""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_int(value: str | None, default: int) -> int:
    """容错解析整数环境变量"""
    try:
        return int(value) if value else default
    except ValueError:
        return default


def _load_dotenv() -> None:
    """轻量级 .env 加载器（不依赖 python-dotenv）。

    只解析简单的 KEY=VALUE 行，支持 # 注释。
    """
    env_file = ROOT_DIR / "config" / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("\"'")
        # 不覆盖已存在的环境变量（命令行优先级最高）
        if key and key not in os.environ:
            os.environ[key] = value


# 模块加载时立即解析 .env
_load_dotenv()


@dataclass(frozen=True)
class Settings:
    """全局配置单例。读取顺序：os.environ → .env → 默认值。"""

    # ---------- 被测应用 ----------
    base_url: str = field(
        default_factory=lambda: os.environ.get("BASE_URL", "http://127.0.0.1:5000")
    )

    # ---------- 浏览器 ----------
    browser: str = field(
        default_factory=lambda: os.environ.get("BROWSER", "chromium")
    )
    headless: bool = field(
        default_factory=lambda: _parse_bool(os.environ.get("HEADLESS"), True)
    )
    slow_mo: int = field(
        default_factory=lambda: _parse_int(os.environ.get("SLOW_MO"), 0)
    )
    viewport_width: int = field(
        default_factory=lambda: _parse_int(os.environ.get("VIEWPORT_WIDTH"), 1280)
    )
    viewport_height: int = field(
        default_factory=lambda: _parse_int(os.environ.get("VIEWPORT_HEIGHT"), 720)
    )

    # ---------- 超时（毫秒）----------
    default_timeout: int = field(
        default_factory=lambda: _parse_int(os.environ.get("DEFAULT_TIMEOUT"), 30000)
    )
    navigation_timeout: int = field(
        default_factory=lambda: _parse_int(os.environ.get("NAV_TIMEOUT"), 30000)
    )

    # ---------- 并发与重试 ----------
    parallel_workers: str = field(
        default_factory=lambda: os.environ.get("PARALLEL_WORKERS", "auto")
    )
    reruns: int = field(
        default_factory=lambda: _parse_int(os.environ.get("RERUNS"), 0)
    )

    # ---------- 日志 ----------
    log_level: str = field(
        default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO")
    )
    log_dir: Path = field(
        default_factory=lambda: ROOT_DIR / os.environ.get("LOG_DIR", "logs")
    )

    # ---------- Allure ----------
    allure_results_dir: Path = field(
        default_factory=lambda: ROOT_DIR / "allure-results"
    )

    # ---------- 测试账号（敏感信息走环境变量，不硬编码）----------
    admin_username: str = field(
        default_factory=lambda: os.environ.get("ADMIN_USERNAME", "admin")
    )
    admin_password: str = field(
        default_factory=lambda: os.environ.get("ADMIN_PASSWORD", "admin123")
    )
    editor_username: str = field(
        default_factory=lambda: os.environ.get("EDITOR_USERNAME", "editor")
    )
    editor_password: str = field(
        default_factory=lambda: os.environ.get("EDITOR_PASSWORD", "edit456")
    )
    viewer_username: str = field(
        default_factory=lambda: os.environ.get("VIEWER_USERNAME", "viewer")
    )
    viewer_password: str = field(
        default_factory=lambda: os.environ.get("VIEWER_PASSWORD", "view789")
    )

    # ---------- 派生属性 ----------
    @property
    def viewport(self) -> dict:
        return {"width": self.viewport_width, "height": self.viewport_height}

    @property
    def login_url(self) -> str:
        return f"{self.base_url}/login"

    @property
    def dashboard_url(self) -> str:
        return f"{self.base_url}/dashboard"

    def account(self, role: str) -> tuple[str, str]:
        """按角色取账号：role ∈ {admin, editor, viewer}"""
        mapping = {
            "admin": (self.admin_username, self.admin_password),
            "editor": (self.editor_username, self.editor_password),
            "viewer": (self.viewer_username, self.viewer_password),
        }
        if role not in mapping:
            raise ValueError(f"未知角色: {role}，可选: {list(mapping)}")
        return mapping[role]


# 全局单例
settings = Settings()
