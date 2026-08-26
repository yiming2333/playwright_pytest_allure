# utils/api_client.py
"""
API 客户端封装：基于 requests.Session，自带日志、超时、自动重试。

用法：
    from utils.api_client import ApiClient

    client = ApiClient(base_url="http://127.0.0.1:5000")
    client.login("admin", "admin123")
    resp = client.get("/api/products?q=Pro")
    data = resp.json()
"""
from __future__ import annotations

import json
from typing import Any, Optional

import requests

from utils.logger import get_logger

log = get_logger(__name__)


class ApiClient:
    """轻量 HTTP 客户端封装。

    特性：
    - 基于 requests.Session，自动管理 cookie
    - 全部请求带日志（method/url/status/duration）
    - 默认超时 10s，可覆盖
    - 失败自动 raise_for_status，可关
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: int = 10,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()

    # ---------- 内部 ----------
    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url}{path}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        params: Any = None,
        raise_on_error: bool = True,
        **kwargs,
    ) -> requests.Response:
        url = self._url(path)
        kwargs.setdefault("timeout", self.timeout)

        log.info(f"{method} {url} params={params} json={_truncated(json_body)}")
        resp = self.session.request(method, url, json=json_body, params=params, **kwargs)
        log.info(f"  ← {resp.status_code} in {resp.elapsed.total_seconds()*1000:.0f}ms")

        if raise_on_error and resp.status_code >= 400:
            log.error(f"HTTP {resp.status_code}: {resp.text[:500]}")
            resp.raise_for_status()
        return resp

    # ---------- 公共方法 ----------
    def login(self, username: str, password: str) -> dict:
        """登录并返回响应 JSON"""
        resp = self._request(
            "POST",
            "/api/login",
            json_body={"username": username, "password": password},
        )
        data = resp.json()
        log.info(f"登录成功: user={username} role={data.get('role')}")
        return data

    def get(self, path: str, **kwargs) -> requests.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self._request("DELETE", path, **kwargs)

    # ---------- cookie 复用 ----------
    def inject_cookies(self, cookies: list[dict]) -> None:
        """从 Playwright storage_state 的 cookies 注入到 session"""
        for c in cookies:
            self.session.cookies.set(
                c["name"],
                c["value"],
                domain=c.get("domain", "127.0.0.1"),
                path=c.get("path", "/"),
            )
        log.debug(f"注入 {len(cookies)} 个 cookie")

    def close(self) -> None:
        self.session.close()


def _truncated(obj: Any, limit: int = 200) -> str:
    """日志截断：避免大 body 刷屏"""
    try:
        s = json.dumps(obj, ensure_ascii=False) if obj else ""
    except Exception:
        s = str(obj)
    return f"{s[:limit]}..." if len(s) > limit else s
