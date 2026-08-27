# 【关键】锁定具体版本号，不要用 latest！
# latest 会导致某天构建突然失败，因为上游更新了浏览器或Python版本
FROM mcr.m.daocloud.io/playwright/python:v1.62.0-noble

# ✅ ENV 必须在 FROM 之后
ENV BASE_URL=http://127.0.0.1:5000
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
# 设置工作目录
WORKDIR /app

# 【性能优化】先复制 requirements.txt 并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 使用 JSON 数组格式（exec form）
CMD ["pytest", "--headed=False", "-v"]