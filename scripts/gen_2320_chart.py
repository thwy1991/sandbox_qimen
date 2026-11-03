# -*- coding: utf-8 -*-
"""生成 2026-06-08 23:20 子时奇门盘"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from generate_qimen_image import get_all_gz, get_bureau_info, draw_qimen_chart
from qimen_engine_v2 import solve

dt = datetime(2026, 6, 8, 23, 20)
year_gz, month_gz, day_gz, hour_gz = get_all_gz(dt)
jieqi, dun, bureau, yuan = get_bureau_info(dt)
result = solve(year_gz, month_gz, day_gz, hour_gz, jieqi, dun, bureau)

ci = result['chart_info']
print('=' * 60)
print('2026年6月8日 23:20 (子时)')
print('=' * 60)
print('四柱:', year_gz, month_gz, day_gz, hour_gz)
print('局数:', jieqi + yuan, dun + '遁' + str(bureau) + '局')
print('值符:', ci['zhi_fu_star'], '落', ci['zhi_fu_heaven_pos'], '宫')
print('值使:', ci['zhi_shi_door'], '落', ci['zhi_shi_pos'], '宫')
print('旬首:', ci['xun_shou_gan'], '在', ci['zhi_fu_pos'], '宫')
print('旬空:', ci['kong_pair'], '->', ci['kong_palaces'], '宫')
print('马星:', ci['ma_zhi'], '(', ci['ma_palace'], '宫)')

dp = result['di_pan']
hv = result['hv_stems']
doors = result['palace_doors']
gods = result['palace_gods']
stars = result['hv_stars']

print()
for p in range(1, 10):
    if p == 5:
        continue
    print('%d宫 | 地盘:%s 天盘:%s | %s | %s | %s' % (
        p, dp.get(p, '?'), hv.get(p, '?'),
        gods.get(p, '?'), stars.get(p, '?'), doors.get(p, '?')
    ))

dt_str = dt.strftime('%Y年%m月%d日 %H:%M')
out = draw_qimen_chart(
    result,
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'output', 'qimen_20260608_2320.png'),
    dt_str=dt_str, jieqi=jieqi, dun=dun, bureau_num=bureau, yuan=yuan
)
print()
print('图片已保存:', out)
