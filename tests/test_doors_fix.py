# -*- coding: utf-8 -*-
"""验证八门视觉顺时针修复"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from qimen_engine_v2 import solve

print('=' * 60)
print('=== 文档案例验证: 阳遁6局 甲戌旬(#10)->7宫(己在7) 庚辰(#16) 步数6 值使惊门落4宫 ===')
# 文档: 甲戌藏于己, 己在兑七宫, 阳遁顺数7->8->9->1->2->3->4(第7位)=巽四宫
r = solve('己亥', '辛未', '丁卯', '庚辰', '大暑', '阳', 6)
doors = {k: v for k, v in sorted(r['palace_doors'].items()) if v}
print('地盘:', {k: v for k, v in sorted(r['di_pan'].items())})
print('旬首干:', r['chart_info']['xun_shou_gan'])
print('八门结果:', doors)
print('值使落宫:', r['chart_info']['zhi_shi_pos'])

# 文档期望: 4:惊, 9:开, 2:休, 7:生, 6:伤, 1:杜, 8:景, 3:死
expected = {1: '杜门', 2: '休门', 3: '死门', 4: '惊门', 6: '伤门', 7: '生门', 8: '景门', 9: '开门'}
ok = all(doors.get(k) == v for k, v in expected.items())
print(f'验证: {"PASS" if ok else "FAIL"}')
if not ok:
    for k, v in expected.items():
        got = doors.get(k, '?')
        if got != v:
            print(f'  宫{k}: 期望{v} 得到{got}')

print()
print('=== 文档案例验证: 阴遁 甲子旬(#0)->1宫 丁卯(#3) 值使休门落7宫 ===')
# 地盘(阴遁某局,1宫=戊): 甲子旬->甲子藏于戊
# 阴遁逆数1->9->8->7(第4位)=兑七宫
r2 = solve('己亥', '辛未', '丁卯', '丁卯', '大暑', '阴', 1)
doors2 = {k: v for k, v in sorted(r2['palace_doors'].items()) if v}
print('地盘:', {k: v for k, v in sorted(r2['di_pan'].items())})
print('旬首干:', r2['chart_info']['xun_shou_gan'])
print('八门结果:', doors2)
print('值使落宫:', r2['chart_info']['zhi_shi_pos'])

print()
print('=== 当前时间排盘: 2026-06-07 09:27 阳遁6局 ===')
r3 = solve('丙午', '甲午', '壬子', '乙巳', '芒种', '阳', 6)
doors3 = {k: v for k, v in sorted(r3['palace_doors'].items()) if v}
print('八门结果:', doors3)
print('值符:', r3['chart_info']['zhi_fu_star'], '落', r3['chart_info']['zhi_fu_heaven_pos'], '宫')
print('值使:', r3['chart_info']['zhi_shi_door'], '落', r3['chart_info']['zhi_shi_pos'], '宫')
