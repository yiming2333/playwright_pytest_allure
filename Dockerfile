# 【关键】锁定具体版本号，不要用 latest！
# latest 会导致某天构建突然失败，因为上游更新了浏览器或Python版本
FROM mcr.microsoft.com/playwright/python:v1.48.0-noble

# 设置工作目录
WORKDIR /app

# 【性能优化】先复制 requirements.txt 并安装依赖
# 利用 Docker 层缓存：只要 requirements.txt 没变，这层就不会重新构建
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 【关键】确认 Playwright 浏览器已就绪
# 官方 python 镜像通常已内置浏览器，但如果你修改了基础镜像或升级了 playwright 版本，
# 可能需要显式安装。加上这行更保险：
# RUN playwright install --with-deps chromium

# 复制项目代码（此时 .dockerignore 会生效，排除无关文件）
COPY . .

# 使用 JSON 数组格式（exec form），避免 shell 信号传递问题
# headed=False 是默认值，在容器中必须用 headless 模式
CMD ["pytest", "--headed=False", "-v"]