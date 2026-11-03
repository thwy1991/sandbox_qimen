# -*- coding: utf-8 -*-
"""调试八门排盘逻辑"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qimen_engine_v2 import (
    solve, calc_doors, get_di_pan, jiazi_pos, get_xun_shou_gan,
    DOORS_BY_PALACE, DOOR_NUM_SEQ, DOOR_NUM_RSEQ, CLOCKWISE_8
)

# DOOR_ORDER is defined inside calc_doors, replicate here
DOOR_ORDER = ['休门','生门','伤门','杜门','景门','死门','惊门','开门']
from generate_qimen_image import get_all_gz, get_bureau_info
from datetime import datetime

dt = datetime(2026, 6, 8, 21, 20)
year_gz, month_gz, day_gz, hour_gz = get_all_gz(dt)
print(f'四柱: {year_gz} {month_gz} {day_gz} {hour_gz}')

jieqi, dun, bureau, yuan = get_bureau_info(dt)
print(f'局数: {dun}遁{bureau}局 {jieqi}{yuan}')

result = solve(year_gz, month_gz, day_gz, hour_gz, jieqi, dun, bureau)
ci = result['chart_info']
print(f'地盘: {dict(sorted(result["di_pan"].items()))}')
print(f'天盘: {dict(sorted(result["hv_stems"].items()))}')
print(f'八门: {dict(sorted(result["palace_doors"].items()))}')
print(f'旬首干: {ci["xun_shou_gan"]}, 旬首宫: {ci["zhi_fu_pos"]}')
print(f'值符: {ci["zhi_fu_star"]}落{ci["zhi_fu_heaven_pos"]}宫')
print(f'值使: {ci["zhi_shi_door"]}落{ci["zhi_shi_pos"]}宫')
print(f'小时甲子序号: {jiazi_pos(hour_gz[0], hour_gz[1])}')

# 详细计算八门
di_pan = result['di_pan']
xun_shou_gan = ci['xun_shou_gan']
xun_shou_pos = ci['zhi_fu_pos']
hour_gan, hour_zhi = hour_gz[0], hour_gz[1]
print(f'\n=== 八门详细计算 ===')
print(f'旬首干={xun_shou_gan}, 旬首在地盘宫位={xun_shou_pos}')
print(f'时干={hour_gan}, 时支={hour_zhi}')

# 逐步调试 calc_doors
start_p = xun_shou_pos if xun_shou_pos != 5 else 2
zhi_shi_door = DOORS_BY_PALACE.get(start_p, '休门')
print(f'值使门(旬首宫固定门): {zhi_shi_door}')

hour_jiazi = jiazi_pos(hour_gan, hour_zhi)
xun_jiazi_start = (hour_jiazi // 10) * 10
steps = hour_jiazi - xun_jiazi_start
print(f'时柱甲子序号={hour_jiazi}, 旬首序号={xun_jiazi_start}, 步数={steps}')

path = DOOR_NUM_SEQ
si_start = path.index(start_p)
print(f'DOOR_NUM_SEQ={path}, start_p={start_p}, si_start={si_start}')
zhi_shi_palace = path[(si_start + steps) % 8]
print(f'值使落宫: path[({si_start}+{steps})%8] = path[{(si_start + steps) % 8}] = {zhi_shi_palace}')

door_si = DOOR_ORDER.index(zhi_shi_door)
si_val = CLOCKWISE_8.index(zhi_shi_palace)
print(f'DOOR_ORDER={DOOR_ORDER}')
print(f'door_si(值使门序)={door_si}, si_val(CLOCKWISE起点)={si_val}')
print(f'CLOCKWISE_8={CLOCKWISE_8}')
print()
for step in range(8):
    target = CLOCKWISE_8[(si_val + step) % 8]
    door = DOOR_ORDER[(door_si + step) % 8]
    marker = ' <--值使' if step == 0 else ''
    print(f'  step {step}: {target}宫 -> {door}{marker}')
