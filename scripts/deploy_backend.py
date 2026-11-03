# -*- coding: utf-8 -*-
"""
奇门遁甲排盘API服务部署脚本

使用方法：
1. 在项目根目录创建虚拟环境：python -m venv .venv
2. 激活虚拟环境后运行本脚本：python scripts/deploy_backend.py
"""

import os
import sys
import subprocess

def main():
    backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
    venv_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.venv')

    # 判断操作系统
    is_windows = sys.platform == 'win32'
    pip_cmd = os.path.join(venv_dir, 'Scripts', 'pip.exe') if is_windows else os.path.join(venv_dir, 'bin', 'pip')
    python_cmd = os.path.join(venv_dir, 'Scripts', 'python.exe') if is_windows else os.path.join(venv_dir, 'bin', 'python')

    # 安装依赖
    req_file = os.path.join(backend_dir, 'requirements.txt')
    print(f'[1/3] 安装依赖: {req_file}')
    subprocess.run([pip_cmd, 'install', '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple', '-r', req_file], check=True)

    # 测试启动
    print('[2/3] 测试API启动...')
    app_file = os.path.join(backend_dir, 'app.py')
    print(f'  启动命令: {python_cmd} {app_file}')
    print('  本地测试地址: http://127.0.0.1:5000/api/health')

    print('[3/3] 部署说明:')
    print('  本地开发: 直接运行 python backend/app.py')
    print('  生产部署: gunicorn -c backend/gunicorn.conf.py backend.app:app')
    print('  微信小程序: 修改 miniprogram/app.js 中的 apiBase 为你的域名')

if __name__ == '__main__':
    main()
