# 【关键】锁定具体版本号，不要用 latest！
# latest 会导致某天构建突然失败，因为上游更新了浏览器或Python版本
FROM playwright-base:v1.62.0
# BASE_URL 由 docker-compose.yml 的环境变量注入，此处不设置默认值
# 复制项目代码
COPY . .

# 使用 JSON 数组格式（exec form）
CMD ["pytest", "--headed=False", "-v"]