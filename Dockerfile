# -*- coding: utf-8 -*-
# 奇门遁甲排盘后端 Dockerfile - 微信云托管 CloudRun
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置时区为中国时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目代码
COPY . .

# 暴露端口（云托管会自动注入PORT环境变量）
EXPOSE 80

# 使用gunicorn生产级启动
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--timeout", "120", "backend.app:app"]
