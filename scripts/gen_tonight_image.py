# -*- coding: utf-8 -*-
"""生成2026年6月8日 21:20 亥时奇门盘图"""
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate_qimen_image import get_all_gz, get_bureau_info, draw_qimen_chart
from qimen_engine_v2 import solve

dt = datetime(2026, 6, 8, 21, 20)
ygz, mgz, dgz, hgz = get_all_gz(dt)
jq, dun, bureau, yuan = get_bureau_info(dt)
result = solve(ygz, mgz, dgz, hgz, jq, dun, bureau)

dt_str = dt.strftime('%Y年%m月%d日 %H:%M')
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_path = os.path.join(project_root, 'output', 'qimen_20260608_2120.png')

draw_qimen_chart(result, output_path, dt_str=dt_str, jieqi=jq, dun=dun, bureau_num=bureau, yuan=yuan)
print(f'图片已生成: {output_path}')
