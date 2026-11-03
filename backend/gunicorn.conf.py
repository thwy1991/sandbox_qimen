# -*- coding: utf-8 -*-
"""
Gunicorn 配置文件
用于生产环境部署奇门遁甲排盘API
"""

import os

bind = '0.0.0.0:5000'
workers = 2
worker_class = 'sync'
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
loglevel = 'info'
accesslog = '-'
errorlog = '-'
proc_name = 'qimen-api'
