# Dockerfile.base
FROM mcr.m.daocloud.io/playwright/python:v1.62.0-noble

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app

# 只复制依赖文件并安装（这一层会被缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# BASE_URL 由 docker-compose.yml 的环境变量注入，此处不设置默认值
# 复制项目代码
COPY . .

# 使用 JSON 数组格式（exec form）
CMD ["pytest", "--headed=False", "-v"]