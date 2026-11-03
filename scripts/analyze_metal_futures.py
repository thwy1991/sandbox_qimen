# -*- coding: utf-8 -*-
"""
金属期货夜盘奇门遁甲分析
时间：2026年6月8日 22:00（亥时）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from generate_qimen_image import get_all_gz, get_bureau_info
from qimen_engine_v2 import solve
from scripts.market_analysis import analyze_market, get_key_palace_info, is_wu_bu_yu_shi, WUXING

dt = datetime(2026, 6, 8, 22, 0)
year_gz, month_gz, day_gz, hour_gz = get_all_gz(dt)
jieqi, dun, bureau, yuan = get_bureau_info(dt)
result = solve(year_gz, month_gz, day_gz, hour_gz, jieqi, dun, bureau)
ci = result['chart_info']
info = get_key_palace_info(result)
trend, signals = analyze_market(result)

print('=' * 80)
print('金属期货夜盘奇门分析')
print('时间: 2026年6月8日 22:00 (亥时)')
print('=' * 80)
print(f'四柱: {year_gz} {month_gz} {day_gz} {hour_gz}')
print(f'局数: {jieqi}{yuan} {dun}遁{bureau}局')
print(f'旬首: {ci["xun_shou_gan"]} 在{ci["zhi_fu_pos"]}宫')
print(f'值符: {ci["zhi_fu_star"]} 落{ci["zhi_fu_heaven_pos"]}宫')
print(f'值使: {ci["zhi_shi_door"]} 落{ci["zhi_shi_pos"]}宫')
print(f'旬空: {ci["kong_pair"]} -> {ci["kong_palaces"]}宫')
print(f'马星: {ci["ma_zhi"]}({ci["ma_palace"]}宫)')
print()

dp = result['di_pan']
hv = result['hv_stems']
doors = result['palace_doors']
gods = result['palace_gods']
stars = result['hv_stars']

# 五行映射：金→金属
WX_METAL = {
    '金': '直接利好（金属属金）',
    '土': '支撑利好（土生金）',
    '火': '克金利空（火克金）',
    '水': '泄金属性（金生水）',
    '木': '中性偏弱（金克木）',
}

print('-' * 80)
print('完整盘面:')
for p in range(1, 10):
    if p == 5:
        continue
    kw = WUXING[p]
    metal_hint = WX_METAL.get(kw, '')
    print(f'  {p}宫({kw}) [{metal_hint}]')
    print(f'    地盘:{dp.get(p,"?")} 天盘:{hv.get(p,"?")} 八神:{gods.get(p,"?")} 九星:{stars.get(p,"?")} 八门:{doors.get(p,"?")}')
print()

print('-' * 80)
print('关键宫位分析:')
hour_pos = info['hour_gan_pos']
day_pos = info['day_gan_pos']
wu_pos = info['wu_pos']
sheng_pos = info['sheng_pos']
kai_pos = info['kai_pos']

print(f'  时干({info["hour_gan"]})落{hour_pos}宫({WUXING[hour_pos] if hour_pos else "?"})     -> 事体/当前状态')
print(f'  日干({info["day_gan"]})落{day_pos}宫({WUXING[day_pos] if day_pos else "?"})     -> 大盘主体')
print(f'  天盘戊落{wu_pos}宫({WUXING[wu_pos] if wu_pos else "?"})     -> 资金面')
print(f'  生门落{sheng_pos}宫({WUXING[sheng_pos] if sheng_pos else "?"})     -> 生机财利')
print(f'  开门落{kai_pos}宫({WUXING[kai_pos] if kai_pos else "?"})     -> 通畅上扬')
print(f'  值符落{ci["zhi_fu_heaven_pos"]}宫({WUXING[ci["zhi_fu_heaven_pos"]]}) -> 主力态度')
print(f'  值使落{ci["zhi_shi_pos"]}宫({WUXING[ci["zhi_shi_pos"]]}) -> 执行方向')
print()

# 金属期货五行专项分析
print('-' * 80)
print('金属期货五行专项分析:')
print()

# 分析关键宫五行
key_palaces = []
if hour_pos: key_palaces.append(('时干(事体)', hour_pos, WUXING[hour_pos]))
if day_pos: key_palaces.append(('日干(主体)', day_pos, WUXING[day_pos]))
if wu_pos: key_palaces.append(('天盘戊(资金)', wu_pos, WUXING[wu_pos]))
if sheng_pos: key_palaces.append(('生门(生机)', sheng_pos, WUXING[sheng_pos]))
if kai_pos: key_palaces.append(('开门(通畅)', kai_pos, WUXING[kai_pos]))
key_palaces.append(('值符(主力)', ci['zhi_fu_heaven_pos'], WUXING[ci['zhi_fu_heaven_pos']]))
key_palaces.append(('值使(执行)', ci['zhi_shi_pos'], WUXING[ci['zhi_shi_pos']]))

metal_score = 0  # 利好金属分数
for name, palace, wx in key_palaces:
    god = gods.get(palace, '')
    star = stars.get(palace, '')
    door = doors.get(palace, '')
    
    metal_effect = ''
    if wx == '金':
        metal_effect = '【直接利好金属】'
        metal_score += 2
    elif wx == '土':
        metal_effect = '【土生金，支撑利好】'
        metal_score += 1
    elif wx == '火':
        metal_effect = '【火克金，利空金属】'
        metal_score -= 1
    elif wx == '水':
        metal_effect = '【金生水，泄金属性】'
        metal_score -= 1
    else:
        metal_effect = '【中性】'
    
    kong_mark = ' [逢空!!!]' if palace in ci['kong_palaces'] else ''
    print(f'  {name}: {palace}宫({wx}) {god} {star} {door}{kong_mark}')
    print(f'    金属含义: {metal_effect}')

print()

# 空亡对金属的影响
kong_palaces = ci['kong_palaces']
for kp in kong_palaces:
    if kp in [p for _, p, _ in key_palaces]:
        print(f'  [!] 空亡宫{kp}({WUXING[kp]})影响关键宫位，能量减弱')

# 马星
ma_palace = ci['ma_palace']
ma_wx = WUXING[ma_palace]
ma_god = gods.get(ma_palace, '')
ma_door = doors.get(ma_palace, '')
print(f'  马星: {ma_palace}宫({ma_wx}) {ma_god} {ma_door} -> 异动方向')

print()
print('金属综合评分:', metal_score, '/ 14')
if metal_score >= 4:
    metal_trend = '偏强看涨'
elif metal_score >= 1:
    metal_trend = '震荡偏强'
elif metal_score >= -2:
    metal_trend = '震荡'
elif metal_score >= -5:
    metal_trend = '偏弱看跌'
else:
    metal_trend = '看跌'

# 五不遇时检测
is_wby, wby_msg = is_wu_bu_yu_shi(info['day_gan'], info['hour_gan'])
print()

print('=' * 80)
print('分析信号:')
for s in signals:
    print(f'  {s}')
print()
print(f'大盘综合趋势: 【{trend}】')
print(f'金属专项趋势: 【{metal_trend}】(评分: {metal_score})')
if is_wby:
    print(f'警告: {wby_msg}')
print('=' * 80)
