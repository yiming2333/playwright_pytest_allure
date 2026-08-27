# utils/api_client.py
from __future__ import annotations

import json
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from utils.logger import get_logger

log = get_logger(__name__)

_SENSITIVE_KEYS = {"password", "passwd", "pwd", "token", "secret", "authorization"}


class ApiClient:
    """轻量 HTTP 客户端封装 - 稳定版"""

    def __init__(
        self,
        base_url: str = "",
        timeout: int = 10,
        max_retries: int = 3,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

        # 自动重试
        if max_retries > 0:
            retry = Retry(
                total=max_retries,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504],
                allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
            )
            adapter = HTTPAdapter(max_retries=retry)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)

    # ---------- 核心：直接用登录替代 cookie 注入 ----------
    def login(self, username: str, password: str) -> dict:
        """登录并自动保持会话（Session 自动管理 Set-Cookie）"""
        resp = self._request(
            "POST", "/api/login",
            json_body={"username": username, "password": password},
        )
        data = resp.json()
        log.info(f"✅ 登录成功: user={username} role={data.get('role')}")
        return data

    # ---------- 如果确实需要注入（兜底方案）----------
    def inject_cookies(self, cookies: list[dict]) -> None:
        """
        极简注入：只用 name + value + path，放弃 domain 控制。
        让 requests 根据当前请求 URL 自行匹配。
        """
        for c in cookies:
            # ✅ 不设 domain！让 requests 按请求 URL 自动绑定
            self.session.cookies.set(c["name"], c["value"], path=c.get("path", "/"))
        log.info(f"✅ 注入 {len(cookies)} 个 cookie（无 domain 模式）")

    # ---------- 内部方法 ----------
    def _url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        return f"{self.base_url}{path}"

    def _request(
        self, method: str, path: str, *,
        json_body: Any = None, params: Any = None,
        raise_on_error: bool = True, **kwargs,
    ) -> requests.Response:
        url = self._url(path)
        kwargs.setdefault("timeout", self.timeout)

        safe_body = _mask_sensitive(json_body)
        log.info(f"{method} {url} params={params} json={_truncated(safe_body)}")

        resp = self.session.request(method, url, json=json_body, params=params, **kwargs)
        log.info(f"  ← {resp.status_code} ({resp.elapsed.total_seconds()*1000:.0f}ms)")

        if raise_on_error and resp.status_code >= 400:
            log.error(f"HTTP {resp.status_code}: {resp.text[:500]}")
            resp.raise_for_status()
        return resp

    def get(self, p: str, **kw) -> requests.Response:    return self._request("GET", p, **kw)
    def post(self, p: str, **kw) -> requests.Response:   return self._request("POST", p, **kw)
    def put(self, p: str, **kw) -> requests.Response:    return self._request("PUT", p, **kw)
    def delete(self, p: str, **kw) -> requests.Response: return self._request("DELETE", p, **kw)

    def close(self) -> None:
        self.session.close()


def _mask_sensitive(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: "***" if k.lower() in _SENSITIVE_KEYS else _mask_sensitive(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_mask_sensitive(i) for i in obj]
    return obj

def _truncated(obj: Any, limit: int = 200) -> str:
    try:
        s = json.dumps(obj, ensure_ascii=False) if obj else ""
    except Exception:
        s = str(obj)
    return f"{s[:limit]}..." if len(s) > limit else s