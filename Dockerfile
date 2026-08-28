FROM mcr.m.daocloud.io/playwright/python:v1.62.0-noble

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 默认命令带报告输出
CMD ["pytest", "--headed=False", "-v", "--html=/app/reports/report.html", "--self-contained-html"]