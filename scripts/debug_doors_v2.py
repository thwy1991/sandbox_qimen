# -*- coding: utf-8 -*-
"""逐步追踪2026-06-08 21:20 值使计算"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from qimen_engine_v2 import (
    solve, calc_doors, get_di_pan, jiazi_pos, get_xun_shou_gan,
    DOORS_BY_PALACE, DOOR_NUM_SEQ, DOOR_NUM_RSEQ, CLOCKWISE_8,
    TIANGAN, DIZHI, XUNHEAD_GAN
)
from generate_qimen_image import get_all_gz, get_bureau_info
from datetime import datetime

DOOR_ORDER = ['休门','生门','伤门','杜门','景门','死门','惊门','开门']

dt = datetime(2026, 6, 8, 21, 20)
year_gz, month_gz, day_gz, hour_gz = get_all_gz(dt)
jieqi, dun, bureau, yuan = get_bureau_info(dt)
result = solve(year_gz, month_gz, day_gz, hour_gz, jieqi, dun, bureau)

ci = result['chart_info']
dp = result['di_pan']
hour_gan, hour_zhi = hour_gz[0], hour_gz[1]

print("=" * 60)
print(f"时间: 2026-06-08 21:20")
print(f"四柱: {year_gz} {month_gz} {day_gz} {hour_gz}")
print(f"局数: {dun}遁{bureau}局 {jieqi}{yuan}")
print()

# 1. 旬首
xun_shou_gan = get_xun_shou_gan(hour_gan, hour_zhi)
print(f"1. 旬首干: {xun_shou_gan}")

# 2. 旬首在地盘的位置
xun_shou_pos = None
for p, g in dp.items():
    if g == xun_shou_gan:
        xun_shou_pos = p
        break
print(f"2. 旬首在地盘宫位: {xun_shou_pos}宫 (地盘{xun_shou_gan}在{xun_shou_pos}宫)")
print(f"   地盘: {dict(sorted(dp.items()))}")

# 3. 甲寅旬验证
XUN_FULL = {v:k for k,v in XUNHEAD_GAN.items()}
xun_start_offset = XUN_FULL.get(xun_shou_gan, 0)
print(f"3. 旬首序号偏移: {xun_start_offset}")

# 4. 时柱在六十甲子中的位置
hour_pos = jiazi_pos(hour_gan, hour_zhi)
print(f"4. 时柱{hour_gz}的甲子序号: {hour_pos}")

# 5. 步数计算
steps = hour_pos - xun_start_offset
print(f"5. 步数 = {hour_pos} - {xun_start_offset} = {steps}")

# 6. 值使门
start_p = xun_shou_pos if xun_shou_pos != 5 else 2
zhi_shi_door = DOORS_BY_PALACE.get(start_p, '休门')
print(f"6. 值使门 = {start_p}宫固定门 = {zhi_shi_door}")

# 7. 路径与步数
path = DOOR_NUM_SEQ
si = path.index(start_p)
print(f"7. 路径: {path}, 起点{start_p}宫在索引{si}")
print(f"   走{steps}步: path[(索引{si}+{steps})%8] = path[{ (si+steps)%8 }] = {path[(si+steps)%8]}宫")

# 8. 手动逐位验证
print()
print("8. 手动逐位排盘 (从旬首宫起，阳遁顺数字序):")
manual_zhi_shi = start_p
for i in range(steps + 1):
    cur = path[(si + i) % 8]
    if i == 0:
        marker = "← 旬首(甲寅)"
    elif i == steps:
        marker = f"← 时柱{hour_gz}"
    else:
        marker = ""
    print(f"   第{i}步: {cur}宫 {marker}")

# 9. 当前代码结果
current_result = path[(si + steps) % 8]
print(f"\n当前计算: 值使{zhi_shi_door}落{current_result}宫")
print(f"用户期望: 值使{zhi_shi_door}落2宫")

# 10. 检查几种可能的步数计算方式
print()
print("=" * 60)
print("尝试不同的步数计算方式:")
print(f"  当前: steps={steps} → 落{path[(si+steps)%8]}宫")

# 方式A: steps-1 (旬首不计)
steps_a = steps - 1
print(f"  A. steps-1={steps_a} (旬首不计) → 落{path[(si+steps_a)%8]}宫")

# 方式B: steps基于地支差
zhi_xun = '寅'  # 甲寅旬
zhi_hour = hour_zhi
zhi_diff = (DIZHI.index(zhi_hour) - DIZHI.index(zhi_xun)) % 12
print(f"  B. 地支差(亥11-寅2)={zhi_diff} → 落{path[(si+zhi_diff)%8]}宫")

# 方式C: 公历算法步数解释 - 从旬首到该柱经过几天
zhi_diff_c = DIZHI.index(zhi_hour) - DIZHI.index(zhi_xun)
if zhi_diff_c < 0:
    zhi_diff_c += 12
print(f"  C. 天干差={steps_a} → 落{path[(si+steps_a)%8]}宫")

# 方式D: 使用天盘顺时针路径而非数字序
si_cw = CLOCKWISE_8.index(start_p)
print(f"  D. 用CLOCKWISE_8={CLOCKWISE_8}, 起点{start_p}索引{si_cw}, {steps}步 → 落{CLOCKWISE_8[(si_cw+steps)%8]}宫")

# 方式E: steps-1 用 CLOCKWISE_8
print(f"  E. CLOCKWISE + steps-1={steps_a} → 落{CLOCKWISE_8[(si_cw+steps_a)%8]}宫")
