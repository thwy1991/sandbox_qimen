# -*- coding: utf-8 -*-
"""
奇门遁甲排盘后端API - Windows服务封装

将Flask后端注册为Windows服务，开机自动启动。
安装:   python scripts\qimen_service.py install
卸载:   python scripts\qimen_service.py remove
启动:   python scripts\qimen_service.py start
停止:   python scripts\qimen_service.py stop
"""

import os
import sys
import win32serviceutil
import win32service
import win32event
import servicemanager

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


class QimenService(win32serviceutil.ServiceFramework):
    _svc_name_ = "QimenAPI"
    _svc_display_name_ = "奇门遁甲排盘API服务"
    _svc_description_ = "奇门遁甲排盘后端Flask API服务，监听端口5000"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.process:
            self.process.terminate()
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.run_flask()

    def run_flask(self):
        # 设置工作目录
        os.chdir(PROJECT_ROOT)
        # 导入并启动Flask应用
        from backend.app import app
        import logging
        logging.basicConfig(
            filename=os.path.join(PROJECT_ROOT, 'logs', 'qimen_service.log'),
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s'
        )
        app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(QimenService)
    else:
        win32serviceutil.HandleCommandLine(QimenService)
