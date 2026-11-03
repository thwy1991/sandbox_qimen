# -*- coding: utf-8 -*-
"""生成今晚 22:00 和 23:30 的奇门盘面图片"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from generate_qimen_image import get_all_gz, get_bureau_info, draw_qimen_chart
from qimen_engine_v2 import solve

times = [
    (datetime(2026, 6, 10, 14, 0),  "14:00 (未时)", "qimen_20260610_1400.png"),
]

for dt, label, filename in times:
    year_gz, month_gz, day_gz, hour_gz = get_all_gz(dt)
    jieqi, dun, bureau, yuan = get_bureau_info(dt)
    result = solve(year_gz, month_gz, day_gz, hour_gz, jieqi, dun, bureau)
    ci = result['chart_info']

    print('=' * 60)
    print(f'时间: {dt.year}年{dt.month}月{dt.day}日 {label}')
    print(f'四柱: {year_gz} {month_gz} {day_gz} {hour_gz}')
    print(f'局数: {jieqi}{yuan} {dun}遁{bureau}局')
    print(f'值符: {ci["zhi_fu_star"]} 落{ci["zhi_fu_heaven_pos"]}宫')
    print(f'值使: {ci["zhi_shi_door"]} 落{ci["zhi_shi_pos"]}宫')
    print(f'旬首: {ci["xun_shou_gan"]} 在{ci["zhi_fu_pos"]}宫')
    print(f'旬空: {ci["kong_pair"]} -> {ci["kong_palaces"]}宫')
    print(f'马星: {ci["ma_zhi"]}({ci["ma_palace"]}宫)')

    dp = result['di_pan']
    hv = result['hv_stems']
    doors = result['palace_doors']
    gods = result['palace_gods']
    stars = result['hv_stars']
    jigan = result['hv_stars_jigan']  # 寄星（天禽）
    jigan_g = result['jigan_stems']  # 寄干
    print()
    for p in range(1, 10):
        if p == 5: continue
        s = stars.get(p, '?')
        js = jigan.get(p, '')
        star_str = s if not js else f'{s}+{js}'  # 如 天芮+天禽
        g = hv.get(p, '?')
        jg = jigan_g.get(p, '')
        gan_str = g if not jg else f'{g}({jg})'  # 如 乙(庚)
        print(f'  {p}宫 | 地:{dp.get(p,"?")} 天:{gan_str} | {gods.get(p,"?"):　<4} | {star_str:　<8} | {doors.get(p,"?")}')

    print()
    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            'output', filename)
    out = draw_qimen_chart(result, out_path,
                          dt_str=f'{dt.year}年{dt.month}月{dt.day}日 {label}',
                          jieqi=jieqi, dun=dun, bureau_num=bureau, yuan=yuan)
    print(f'图片已保存: {out}')

print('=' * 60)
print('完成！')
