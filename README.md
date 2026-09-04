# Playwright + Pytest + Allure 全能测试靶场

一个集 **UI 自动化测试 / API+UI 混合测试 / 多浏览器兼容测试 / 参数化测试 / Allure 报告** 于一体的实战教学项目。配套内置 Flask Mock 应用，无需任何外部依赖即可跑通全部 67 条用例。

按 **Playwright Python 工业级最佳实践** 分层：配置层 / 工具层 / 日志层 / Page Object 层 / 测试层。

---

## 项目亮点

| 能力 | 说明 |
|------|------|
| 67 条端到端用例 | 覆盖 14 类 Playwright 定位器与交互模式（含 dblclick/type/dragDrop/快捷键/导航历史） |
| 73 条用例（含多浏览器展开） | 67 基础 + 6 条高级交互/导航测试 |
| 真·跨浏览器 | chromium / firefox / webkit 三浏览器自动参数化 |
| 参数化 + 数据驱动 | 搜索/表单/登录参数化数据外置到 `config/test_data.json` |
| API+UI 混合 | `ApiClient` 封装 HTTP，先准备数据再用 Playwright 验证 UI |
| 并发隔离 | pytest-xdist 每个 worker 独立浏览器上下文 + 独立日志文件 |
| Allure 报告 | 失败自动截图 + HTML 源码 + 按 Feature/Story/Severity 分组 |
| 三层架构 | config（配置）/ utils（工具+日志）/ pages（PO）分层清晰 |
| Session 登录复用 | 一次登录全 session 复用，API 与 UI 共享同一 token |

---

## 目录结构（分层架构）

```
playwright-pytest-allure/
│
├── config/                       # 【配置层】环境与运行参数
│   ├── __init__.py
│   ├── settings.py               # Settings dataclass：从环境变量/.env 读配置
│   ├── .env.example              # 环境变量模板（复制为 .env 即可）
│   └── test_data.json            # 外置参数化测试数据
│
├── utils/                        # 【工具层 + 日志层】
│   ├── __init__.py
│   ├── logger.py                 # 标准库 logging，控制台+文件双输出
│   ├── screenshot.py             # 失败自动截图 + attach Allure
│   ├── api_client.py             # ApiClient：带日志/超时的 HTTP 客户端
│   └── data_loader.py            # 从 JSON 加载参数化数据
│
├── pages/                        # 【Page Object 层】
│   ├── __init__.py
│   ├── base_page.py              # BasePage：通用导航/等待/日志
│   └── locator_range_page.py     # LocatorRangePage：13 类定位器封装
│
├── tests/                        # 【测试层】
│   ├── __init__.py
│   ├── test_locator_range.py     # 31 条：13 类定位器与交互
│   ├── test_parametrize.py       # 22 条：参数化搜索/表单/登录/购物车
│   ├── test_multi_browser.py     # 12 条：3 浏览器 × 4 场景
│   └── test_api_ui_hybrid.py     #  2 条：API+UI 混合验证
│
├── templates/                    # 被测前端（Flask Jinja2 模板）
│   ├── index.html                # 主靶场页面（13 张卡片）
│   ├── login.html                # 登录页
│   └── dashboard.html           # 受保护仪表盘
│
├── conftest.py                   # Pytest 全局 fixture（集成 config + utils）
├── mock_server.py               # Flask Mock 后端
├── pytest.ini                    # Pytest 配置
├── requirements.txt              # 依赖清单
├── .gitignore
│
├── allure/                       # Allure 静态资源
│   └── environment.properties     # 报告环境信息
├── allure-results/               # Allure 原始结果（gitignore）
├── allure-report/                # Allure HTML 报告（gitignore）
└── logs/                         # 运行日志（gitignore，按 worker 分文件）
```

---

## 三层架构详解

### 1. 配置层 (`config/`)

[config/settings.py](config/settings.py) 用 `dataclass` 定义 `Settings` 单例，读取顺序：

```
环境变量（命令行/CI） > config/.env 文件 > 代码默认值
```

```python
from config import settings

settings.base_url          # http://127.0.0.1:5000
settings.headless          # True
settings.slow_mo           # 0
settings.viewport          # {"width": 1280, "height": 720}
settings.log_level         # INFO
settings.account("admin")  # ("admin", "admin123")
```

**配置项**：`BASE_URL` / `BROWSER` / `HEADLESS` / `SLOW_MO` / `VIEWPORT_*` / `DEFAULT_TIMEOUT` / `PARALLEL_WORKERS` / `RERUNS` / `LOG_LEVEL` / 各角色账号密码。

复制 `config/.env.example` 为 `config/.env` 即可自定义，无需改代码。

### 2. 工具层 (`utils/`)

| 模块 | 职责 | 用法 |
|------|------|------|
| [logger.py](utils/logger.py) | 标准库 logging，控制台+文件双输出，xdist 每 worker 独立日志 | `from utils.logger import get_logger; log = get_logger(__name__)` |
| [screenshot.py](utils/screenshot.py) | 失败自动截图 + HTML 源码，附加到 Allure | 由 conftest 钩子自动调用 |
| [api_client.py](utils/api_client.py) | 基于 requests.Session 的 HTTP 客户端，带日志/超时/cookie 复用 | `client = ApiClient(base_url); client.get("/api/x")` |
| [data_loader.py](utils/data_loader.py) | 从 `config/test_data.json` 加载参数化数据 | `load_params("search_keywords", "keyword", "expected_count")` |

### 3. 日志层（融入 utils/）

[utils/logger.py](utils/logger.py) 设计：

- **控制台 handler**：按 `LOG_LEVEL` 输出（默认 INFO）
- **文件 handler**：DEBUG 全级别，存到 `logs/test_YYYYMMDD.log`
- **并发隔离**：xdist 下每个 worker 写 `logs/test_YYYYMMDD_gwN.log`，避免多进程写同一文件错乱
- **零依赖**：用标准库 `logging`，不引入 loguru

日志样例：
```
2026-08-26 18:19:08 | DEBUG   | pages.base_page | 等待卡片 .result 可见: 8. 进阶大招
2026-08-26 18:19:09 | INFO    | conftest        | 开始 session 级登录: http://127.0.0.1:5000
2026-08-26 18:19:09 | INFO    | utils.api_client | GET /api/products?q=Pro
2026-08-26 18:19:09 | INFO    | utils.api_client |   ← 200 in 12ms
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
# 全量串行
pytest

# 并发执行（推荐，~40s 跑完 67 条）
pytest -n auto

# 失败重试 + 并发
pytest -n auto --reruns 2

# 按标签过滤
pytest -m role                # 只跑 Role 定位测试
pytest -k "search"            # 名字含 search 的用例

# 调试模式（有头 + 慢放）
HEADLESS=false SLOW_MO=100 pytest tests/test_locator_range.py
```

### 4. 生成 / 查看 Allure 报告

```bash
allure generate allure-results -o allure-report --clean
allure open allure-report -p 8088
```

### 5. 查看日志

```bash
# 串行模式
logs/test_YYYYMMDD.log

# 并发模式（每个 worker 一个文件）
logs/test_YYYYMMDD_gw0.log
logs/test_YYYYMMDD_gw1.log
...
```

---

## 配置自定义

复制环境变量模板，按需修改：

```bash
cp config/.env.example config/.env
```

```ini
# config/.env
BASE_URL=http://127.0.0.1:5000
HEADLESS=false           # 本地调试改 false 看浏览器
SLOW_MO=100              # 慢放 100ms 便于观察
LOG_LEVEL=DEBUG          # 看详细日志
PARALLEL_WORKERS=4       # 固定 4 进程并发
```

命令行优先级最高（覆盖 .env）：

```bash
HEADLESS=false SLOW_MO=200 pytest -k login
```

---

## 测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| editor | edit456 | 编辑员 |
| viewer | view789 | 观察者 |

账号密码可通过环境变量覆盖（`ADMIN_USERNAME` / `ADMIN_PASSWORD` 等），生产环境从 CI Secret 注入。

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
session ──> auth_state (登录一次，持久化 storage_state，账号从 settings 读)
              │
              ▼
session ──> browser_context_args (注入登录态 + settings.viewport)
              │                  └─> api_client (复用 auth_state cookie，避免重复登录)
              ▼
function ─> page (pytest-playwright 提供)
              │
              ▼
function ─> navigate_to_home (autouse, goto + localStorage.clear)
              │           └─ 带 @pytest.mark.no_home_navigation 的用例跳过
              ▼
function ─> _screenshot_on_failure (autouse, 失败时调 utils.screenshot)
```

**关键点**：
- `auth_state` 用 pytest-playwright 的 `playwright` fixture，避免 asyncio 事件循环冲突
- `api_client` 复用 `auth_state` 的 cookie，API+UI 混合测试只登录 1 次
- `navigate_to_home` 用绝对 URL（`f"{settings.base_url}/"`），xdist 并发 worker 下稳定

---

## 测试矩阵

| 测试文件 | 用例数 | 覆盖内容 |
|----------|--------|----------|
| `test_locator_range.py` | 39 | Role/Text/Label/Alt/TestID/CSS/XPath/链式/Select/Radio/Hover/iframe/MultiSelect/dblclick/type联想/dragDrop/快捷键/reload/goBack/goForward |
| `test_parametrize.py` | 22 | 搜索关键词×5、搜索过滤×3、注册校验×8、登录角色×3、购物车×2、注册正向×1（数据外置 JSON） |
| `test_multi_browser.py` | 12 | chromium/firefox/webkit × 首页/悬停/iframe/表单 |
| `test_api_ui_hybrid.py` | 2 | API 搜索 + UI 验证、API 登录 + UI 访问（用 ApiClient） |
| **合计** | **73** | |

---

## Allure 注解示例

```python
@allure.feature("参数化测试")
@allure.story("注册表单校验")
@allure.severity(allure.severity_level.CRITICAL)
class TestFormValidation:
    @pytest.mark.parametrize(
        "name, email, password, password2, expected_error",
        load_params("register_validations", "name", "email", "password", "password2", "expected_error"),
        ids=load_ids("register_validations"),
    )
    def test_register_validation(self, page, name, email, password, password2, expected_error):
        ...
```

报告中可按 Feature / Story / Severity 维度过滤查看，失败用例附带页面截图与 HTML 源码。

---

## 性能对比

| 模式 | 耗时 | 备注 |
|------|------|------|
| 串行 | ~80s | `pytest` |
| 并发 `-n auto` | ~41s | 14 worker，约 1.95x 加速 |
| 并发 `-n 4` | ~50s | 4 worker，更稳 |

并发没到 14x 是因为 Playwright 浏览器是重资源，多进程同时启动有 IO/CPU 争用。

---

## 常见问题

**Q: 用例 ID 显示成 `[chromium-\u5168\u90e8\u5546\u54c1]` 而不是中文？**

A: 已在 `pytest.ini` 配置 `disable_test_id_escaping_and_forfeit_all_rights_to_community_support = true`。若仍异常，运行前执行 `chcp 65001` 切到 UTF-8 终端。

**Q: 提示 `Cannot navigate to invalid URL`？**

A: `navigate_to_home` 已改用绝对 URL `f"{settings.base_url}/"`，不依赖 `pytest-base-url` 的 base_url 配置，xdist 并发下也稳定。如仍报错，检查 `BASE_URL` 是否设置正确。

**Q: 提示 `ConnectionRefusedError` 或 `net::ERR_CONNECTION_REFUSED`？**

A: Mock 服务未启动。先 `python mock_server.py` 再跑测试。

**Q: 多浏览器用例报 `Executable doesn't exist`？**

A: 执行 `playwright install chromium firefox webkit` 安装浏览器二进制。

**Q: 怎么确认多浏览器用例真的在跑 firefox/webkit，而不是全跑 chromium？**

A: 两道保险已内置：

1. `conftest.py` 覆写了 `browser_type` fixture 来消费 `indirect=True` 参数化的 `request.param`。pytest-playwright 原生 fixture 只认 `--browser` 命令行参数，会把 indirect 传入的浏览器名静默丢弃（用例 ID 显示 `[chromium-firefox]` 实际却跑 chromium 的经典陷阱）。
2. `test_multi_browser.py` 内置 `_verify_real_browser` 防回归断言：真实启动的浏览器若与用例参数不符，用例立刻失败。

验证方式：跑 `pytest tests/test_multi_browser.py` 后查看 `logs/test_*.log`，应出现 `多浏览器参数化生效: firefox/webkit` 日志行。官方全量三浏览器方式：`pytest --browser chromium --browser firefox --browser webkit`（注意：这会把所有用例都参数化到三个浏览器）。

**Q: 测试很慢？**

A: 默认 `headless=True, slow_mo=0`。若需调试改 `HEADLESS=false SLOW_MO=100`（见 [config/settings.py](config/settings.py)）。

**Q: 怎么切换测试环境？**

A: 改 `config/.env` 里的 `BASE_URL`，或命令行 `BASE_URL=https://test.example.com pytest`。
