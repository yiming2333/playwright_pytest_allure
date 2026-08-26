# Playwright + Pytest + Allure 全能测试靶场

一个集 **UI 自动化测试 / API+UI 混合测试 / 多浏览器兼容测试 / 参数化测试 / Allure 报告** 于一体的实战教学项目。配套内置 Flask Mock 应用，无需任何外部依赖即可跑通全部 67 条用例。

---

## 项目亮点

| 能力 | 说明 |
|------|------|
| 67 条端到端用例 | 覆盖 13 类 Playwright 定位器与交互模式 |
| 真·跨浏览器 | chromium / firefox / webkit 三浏览器自动参数化 |
| 参数化测试 | 搜索/表单校验/多角色登录，共 20+ 数据驱动用例 |
| API+UI 混合 | 先用 requests 准备数据，再用 Playwright 验证 UI |
| 并发隔离 | 每个 context 独立 storage_state，购物车数据互不污染 |
| Allure 报告 | 失败自动截图、按 Feature/Story/Severity 分组 |
| Session 登录复用 | 一次登录全 session 复用，避免每条用例重复登录 |

---

## 目录结构

```
playwright-pytest-allure/
├── conftest.py                  # Pytest 全局 fixture（登录、截图、浏览器配置）
├── mock_server.py               # Flask Mock 后端（提供页面与 API）
├── pytest.ini                   # Pytest 配置（含 Allure 输出、中文 ID）
├── requirements.txt             # 依赖清单
├── .gitignore
│
├── pages/                       # Page Object 层
│   ├── __init__.py
│   ├── base_page.py             # BasePage：通用 .result 等待逻辑
│   └── locator_range_page.py    # LocatorRangePage：13 类定位器封装
│
├── templates/                   # Flask Jinja2 模板（被测前端）
│   ├── index.html               # 主靶场页面（13 张卡片）
│   ├── login.html               # 登录页
│   └── dashboard.html           # 受保护仪表盘
│
├── tests/                       # 测试用例层
│   ├── __init__.py
│   ├── test_locator_range.py    # 33 条：13 类定位器与交互
│   ├── test_parametrize.py      # 22 条：参数化搜索/表单/登录/购物车
│   ├── test_multi_browser.py    # 12 条：3 浏览器 × 4 场景
│   └── test_api_ui_hybrid.py    #  2 条：API+UI 混合验证
│
├── allure/                      # Allure 静态资源
│   └── environment.properties   # 报告环境信息
├── allure-results/              # Allure 原始结果（gitignore）
└── allure-report/               # Allure HTML 报告（gitignore）
```

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium firefox webkit
```

### 2. 启动 Mock 服务

```bash
python mock_server.py
```

访问 [http://127.0.0.1:5000](http://127.0.0.1:5000) 确认页面正常。

### 3. 运行测试

```bash
# 全量
pytest

# 仅跑定位器
pytest tests/test_locator_range.py

# 并发执行（已装 pytest-xdist）
pytest -n auto

# 失败重试（已装 pytest-rerunfailures）
pytest --reruns 2
```

### 4. 生成 / 查看 Allure 报告

```bash
# pytest 已自动输出到 allure-results/
allure generate allure-results -o allure-report --clean
allure open allure-report -p 8088
```

浏览器访问 [http://localhost:8088](http://localhost:8088)。

---

## 测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| editor | edit456 | 编辑员 |
| viewer | view789 | 观察者 |

---

## Mock API 一览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/login | 登录，返回 token + cookie |
| GET | /api/products?q=&category=&min_price=&max_price= | 商品搜索/过滤 |
| GET | /api/userinfo | 当前用户信息（需登录） |

页面路由：`/`、`/login`、`/dashboard`、`/logout`。

---

## Fixture 设计

```
session ──> auth_state (登录一次，持久化 storage_state)
              │
              ▼
session ──> browser_context_args (注入登录态、viewport)
              │
              ▼
function ─> page (pytest-playwright 提供)
              │
              ▼
function ─> navigate_to_home (autouse, goto + localStorage.clear)
              │
              ▼
function ─> _screenshot_on_failure (autouse, 失败截图附加到 Allure)
```

**关键点**：`auth_state` 使用 pytest-playwright 的 `playwright` fixture，而非 `sync_playwright()`，避免与插件自身的 asyncio 事件循环冲突。

---

## 测试矩阵

| 测试文件 | 用例数 | 覆盖内容 |
|----------|--------|----------|
| `test_locator_range.py` | 33 | Role/Text/Label/Alt/TestID/CSS/XPath/链式/Select/Radio/Hover/iframe/MultiSelect |
| `test_parametrize.py` | 22 | 搜索关键词×5、搜索过滤×3、注册校验×8、登录角色×3、购物车×2、注册正向×1 |
| `test_multi_browser.py` | 12 | chromium/firefox/webkit × 首页/悬停/iframe/表单 |
| `test_api_ui_hybrid.py` | 2 | API 搜索 + UI 验证、API 登录 + UI 访问 |
| **合计** | **67** | |

---

## Allure 注解示例

```python
@allure.feature("参数化测试")
@allure.story("注册表单校验")
@allure.severity(allure.severity_level.CRITICAL)
class TestFormValidation:
    @pytest.mark.parametrize("name,email,password,password2,expected_error", [...])
    def test_register_validation(self, page, ...):
        ...
```

报告中可按 Feature / Story / Severity 维度过滤查看，失败用例附带页面截图与 HTML 源码。

---

## 常见问题

**Q: 用例 ID 显示成 `[chromium-\u5168\u90e8\u5546\u54c1]` 而不是中文？**

A: 已在 `pytest.ini` 配置 `disable_test_id_escaping_and_forfeit_all_rights_to_community_support = true`。若仍异常，运行前执行 `chcp 65001` 切到 UTF-8 终端。

**Q: 提示 `ConnectionRefusedError` 或 `net::ERR_CONNECTION_REFUSED`？**

A: Mock 服务未启动。先 `python mock_server.py` 再跑测试。

**Q: 多浏览器用例报 `Executable doesn't exist`？**

A: 执行 `playwright install chromium firefox webkit` 安装浏览器二进制。

**Q: 测试很慢？**

A: 默认 `headless=True, slow_mo=0`。若需调试改为 `headless=False, slow_mo=100`（见 [conftest.py](conftest.py) 的 `browser_type_launch_args`）。
