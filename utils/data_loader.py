# utils/data_loader.py
"""
数据加载器：从 JSON 文件加载参数化测试数据。

用法：
    from utils.data_loader import load_test_data

    cases = load_test_data("search_keywords")
    @pytest.mark.parametrize("case", cases, ids=[c["desc"] for c in cases])
    def test_search(case, page):
        ...
"""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from config.settings import ROOT_DIR

_DATA_FILE = ROOT_DIR / "config" / "test_data.json"


@lru_cache(maxsize=1)
def _load_all() -> dict:
    """加载全部数据（缓存）"""
    if not _DATA_FILE.exists():
        raise FileNotFoundError(f"测试数据文件不存在: {_DATA_FILE}")
    return json.loads(_DATA_FILE.read_text(encoding="utf-8"))


def load_test_data(key: str) -> list[dict]:
    """按 key 加载测试数据。

    Args:
        key: test_data.json 顶层键，如 "search_keywords"

    Returns:
        该 key 下的数据列表（list of dict）
    """
    data = _load_all()
    if key not in data:
        raise KeyError(f"测试数据文件中没有 key='{key}'，可用: {list(data.keys())}")
    return data[key]


def load_params(key: str, *fields: str) -> list[tuple]:
    """加载并展平成 pytest.parametrize 需要的 tuple 列表。

    Args:
        key: test_data.json 顶层键
        *fields: 要取出的字段名，顺序即返回 tuple 顺序

    Returns:
        list of tuple，可直接传给 @pytest.mark.parametrize

    示例：
        # test_data.json: {"search": [{"keyword": "Pro", "expected": 2}, ...]}
        cases = load_params("search", "keyword", "expected")
        @pytest.mark.parametrize("keyword, expected", cases)
        def test_search(keyword, expected, page): ...
    """
    items = load_test_data(key)
    return [tuple(item[f] for f in fields) for item in items]


def load_ids(key: str, id_field: str = "desc") -> list[str]:
    """加载用例 ID 列表（取某字段作为可读 ID）"""
    items = load_test_data(key)
    return [str(item.get(id_field, "")) for item in items]
