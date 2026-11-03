# -*- coding: utf-8 -*-
"""
金融期货（股指期货 IH/IF/IC/IM）夜盘奇门遁甲分析
时间：2026年6月8日 22:50（亥时）
金融期货五行核心：火（市场热度） + 金（资金流动）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from generate_qimen_image import get_all_gz, get_bureau_info
from qimen_engine_v2 import solve
from scripts.market_analysis import (
    analyze_market, get_key_palace_info, is_wu_bu_yu_shi,
    WUXING, GAN_WX, DOOR_MEANING, GOD_MEANING
)

dt = datetime(2026, 6, 8, 22, 50)
year_gz, month_gz, day_gz, hour_gz = get_all_gz(dt)
jieqi, dun, bureau, yuan = get_bureau_info(dt)
result = solve(year_gz, month_gz, day_gz, hour_gz, jieqi, dun, bureau)
ci = result['chart_info']
info = get_key_palace_info(result)
trend, signals = analyze_market(result)

dp = result['di_pan']
hv = result['hv_stems']
doors = result['palace_doors']
gods = result['palace_gods']
stars = result['hv_stars']
earth = result['earth_gods']

# ── 金融期货专用五行映射 ──
# 金融期货=股指期货，核心看 火(热度) + 金(资金)
WX_FINANCIAL = {
    '火': '直接利好（火主热度/多头情绪）',
    '金': '利好资金面（金主资金/流动）',
    '木': '生火利好（木生火，助涨情绪）',
    '土': '中性偏弱（土泄火气）',
    '水': '克火利空（水克火，压制情绪）',
}

print('=' * 80)
print('金融期货（股指 IH/IF/IC/IM）夜盘奇门遁甲分析')
print('时间: 2026年6月8日 22:50 (亥时)')
print('=' * 80)
print(f'四柱: {year_gz} {month_gz} {day_gz} {hour_gz}')
print(f'局数: {jieqi}{yuan} {dun}遁{bureau}局')
print(f'值符: {ci["zhi_fu_star"]} 落{ci["zhi_fu_heaven_pos"]}宫')
print(f'值使: {ci["zhi_shi_door"]} 落{ci["zhi_shi_pos"]}宫')
print(f'旬空: {ci["kong_pair"]} -> {ci["kong_palaces"]}宫')
print(f'马星: {ci["ma_zhi"]}({ci["ma_palace"]}宫)')
print()

# ── 完整盘面 ──
print('─' * 80)
print('完整盘面:')
for p in range(1, 10):
    if p == 5:
        continue
    kw = WUXING[p]
    fin_hint = WX_FINANCIAL.get(kw, '')
    door_meaning = DOOR_MEANING.get(doors.get(p, ''), '')
    god_meaning = GOD_MEANING.get(gods.get(p, ''), '')
    print(f'  {p}宫({kw}) [{fin_hint}]')
    print(f'    地:{dp.get(p,"?")} 天:{hv.get(p,"?")} 神:{gods.get(p,"?")}({god_meaning}) 星:{stars.get(p,"?")} 门:{doors.get(p,"?")}({door_meaning})')
print()

# ── 金融期货专项分析 ──
print('=' * 80)
print('金融期货五行专项分析')
print('=' * 80)

# 1. 火宫分析（市场热度核心）
print('\n【一、火宫分析 - 市场热度/多头情绪】')
fire_palace = 9  # 离宫=火
f_door = doors.get(fire_palace, '')
f_god = gods.get(fire_palace, '')
f_star = stars.get(fire_palace, '')
f_dp = dp.get(fire_palace, '')
f_hv = hv.get(fire_palace, '')
f_earth = earth.get(fire_palace, '')
f_gan_wx = GAN_WX.get(f_hv, '') if f_hv else ''
print(f'  9宫(离火) | 地盘:{f_dp} 天盘:{f_hv}({f_gan_wx}) | 神:{f_god} 星:{f_star} 门:{f_door}')

fire_signals = []
if fire_palace in ci['kong_palaces']:
    fire_signals.append('[!]火宫逢空亡 → 市场热度不足，多头乏力')
if f_door in ['景门', '开门', '生门']:
    fire_signals.append(f'[+]火宫临{f_door} → 利好热度')
elif f_door in ['死门', '惊门', '伤门']:
    fire_signals.append(f'[-]火宫临{f_door} → 压制情绪')
if f_god in ['九天', '值符']:
    fire_signals.append(f'[+]火宫临{f_god} → 强劲上扬预期')
elif f_god in ['玄武', '白虎']:
    fire_signals.append(f'[-]火宫临{f_god} → 虚火/杀跌风险')
if f_gan_wx == '火':
    fire_signals.append('[+]天盘干属火 → 火上加火，热度叠加')
elif f_gan_wx == '水':
    fire_signals.append('[-]天盘干属水 → 水克火，压制热度')
elif f_gan_wx == '木':
    fire_signals.append('[+]天盘干属木 → 木生火，助燃情绪')

for s in fire_signals:
    print(f'    {s}')

# 2. 金宫分析（资金流动核心）
print('\n【二、金宫分析 - 资金流动/成交量】')
for gold_p in [6, 7]:  # 乾=6, 兑=7 均属金
    g_door = doors.get(gold_p, '')
    g_god = gods.get(gold_p, '')
    g_star = stars.get(gold_p, '')
    g_hv = hv.get(gold_p, '')
    g_dp = dp.get(gold_p, '')
    g_gan_wx = GAN_WX.get(g_hv, '') if g_hv else ''
    kong_mark = ' [逢空!]' if gold_p in ci['kong_palaces'] else ''
    
    print(f'  {gold_p}宫(金) | 地盘:{g_dp} 天盘:{g_hv}({g_gan_wx}) | 神:{g_god} 星:{g_star} 门:{g_door}{kong_mark}')
    
    gold_signals = []
    if gold_p in ci['kong_palaces']:
        gold_signals.append('  [!]金宫逢空 → 资金不足')
    if g_door in ['开门', '生门']:
        gold_signals.append(f'  [+]金宫临{g_door} → 资金通畅')
    elif g_door in ['死门', '惊门']:
        gold_signals.append(f'  [-]金宫临{g_door} → 资金受阻')
    if g_god in ['值符', '太阴']:
        gold_signals.append(f'  [+]金宫临{g_god} → 主力资金在场')
    if g_gan_wx == '火':
        gold_signals.append('  [-]火克金 → 情绪过热压制资金')
    elif g_gan_wx == '土':
        gold_signals.append('  [+]土生金 → 资金面有支撑')
    for s in gold_signals:
        print(s)

# 3. 景门分析（市场活跃度，景门是离宫正门，最代表市场景象）
print('\n【三、景门分析 - 市场活跃度/交投情绪】')
jing_palace = None
for p, d in doors.items():
    if d == '景门':
        jing_palace = p
        break
if jing_palace:
    j_wx = WUXING[jing_palace]
    j_god = gods.get(jing_palace, '')
    j_star = stars.get(jing_palace, '')
    j_hv = hv.get(jing_palace, '')
    kong_mark = ' [逢空!]' if jing_palace in ci['kong_palaces'] else ''
    print(f'  景门落{jing_palace}宫({j_wx}) | 天盘:{j_hv} | 神:{j_god} 星:{j_star}{kong_mark}')
    
    if jing_palace == 9:
        print('  [++]景门归位离宫 → 市场活跃度最佳，交投旺盛')
    if j_wx == '火':
        print('  [+]景门落火宫 → 红火景象，活跃看涨')
    elif j_wx == '金':
        print('  [+]景门落金宫 → 行情明朗有方向')
    elif j_wx == '水':
        print('  [-]景门落水宫 → 热度被克，人气不足')
    if jing_palace in ci['kong_palaces']:
        print('  [!]景门逢空 → 活跃度虚浮，量能不足')
    if j_god in ['九天', '值符']:
        print(f'  [+]景门临{j_god} → 强势活跃')
    elif j_god in ['白虎']:
        print(f'  [-]景门临{j_god} → 剧烈波动，有恐慌盘')

# 4. 关键宫位分析
print('\n【四、关键宫位综合研判】')
hour_pos = info['hour_gan_pos']
day_pos = info['day_gan_pos']
wu_pos = info['wu_pos']
sheng_pos = info['sheng_pos']
kai_pos = info['kai_pos']

analysis_items = []
if hour_pos:
    analysis_items.append(('时干(事体)', hour_pos, WUXING[hour_pos],
                          gods.get(hour_pos,''), stars.get(hour_pos,''), doors.get(hour_pos,'')))
if day_pos:
    analysis_items.append(('日干(大盘)', day_pos, WUXING[day_pos],
                          gods.get(day_pos,''), stars.get(day_pos,''), doors.get(day_pos,'')))
if wu_pos:
    analysis_items.append(('天盘戊(资金)', wu_pos, WUXING[wu_pos],
                          gods.get(wu_pos,''), stars.get(wu_pos,''), doors.get(wu_pos,'')))
if sheng_pos:
    analysis_items.append(('生门(生机)', sheng_pos, WUXING[sheng_pos],
                          gods.get(sheng_pos,''), stars.get(sheng_pos,''), doors.get(sheng_pos,'')))
if kai_pos:
    analysis_items.append(('开门(通畅)', kai_pos, WUXING[kai_pos],
                          gods.get(kai_pos,''), stars.get(kai_pos,''), doors.get(kai_pos,'')))

# 金融期货评分系统
fin_score = 0
fin_details = []

for name, palace, wx, god, star, door in analysis_items:
    # 火相关（热度）
    fire_related = False
    gold_related = False
    
    if wx == '火':
        fin_score += 2
        fin_details.append(f'[+2] {name}: {palace}宫({wx}) → 直接利好金融期货')
        fire_related = True
    elif wx == '金':
        fin_score += 1
        fin_details.append(f'[+1] {name}: {palace}宫({wx}) → 资金面利好')
        gold_related = True
    elif wx == '木':
        fin_score += 1
        fin_details.append(f'[+1] {name}: {palace}宫({wx}) → 木生火，间接利好')
    elif wx == '土':
        fin_score += 0
        fin_details.append(f'[ 0] {name}: {palace}宫({wx}) → 土泄火气，中性')
    elif wx == '水':
        fin_score -= 1
        fin_details.append(f'[-1] {name}: {palace}宫({wx}) → 水克火，压制多头')
    
    # 门的影响
    if door in ['开门', '生门', '景门']:
        fin_score += 1
        fin_details.append(f'  [+1] 临吉门{door}')
    elif door in ['死门', '惊门']:
        fin_score -= 1
        fin_details.append(f'  [-1] 临凶门{door}')
    
    # 神的影响
    if god in ['九天', '值符']:
        fin_score += 1
        fin_details.append(f'  [+1] 临吉神{god}')
    elif god in ['白虎', '玄武']:
        fin_score -= 1
        fin_details.append(f'  [-1] 临凶神{god}')
    
    # 空亡
    if palace in ci['kong_palaces']:
        fin_score -= 2
        fin_details.append(f'  [-2] 逢空亡，能量大减')
    
    kong_mark = ' [逢空!]' if palace in ci['kong_palaces'] else ''
    print(f'  {name}: {palace}宫({wx}) {god} {star} {door}{kong_mark}')

print()
for d in fin_details:
    print(f'  {d}')

# 马星影响
ma_p = ci['ma_palace']
ma_wx = WUXING[ma_p]
ma_god = gods.get(ma_p, '')
ma_door = doors.get(ma_p, '')
print(f'\n  马星: {ma_p}宫({ma_wx}) {ma_god} {ma_door}')
if ma_wx == '火':
    fin_score += 1
    print('    马星在火宫 → 热度加速扩散')
elif ma_wx == '金':
    print('    马星在金宫 → 资金快速流动')
elif ma_wx == '水':
    fin_score -= 1
    print('    马星在水宫 → 热度被浇灭趋势')

# 五不遇时
is_wby, wby_msg = is_wu_bu_yu_shi(info['day_gan'], info['hour_gan'])
print()

print('=' * 80)
print('金融期货综合评分:', fin_score, '/ ~20')
if is_wby:
    print(f'[!!] 五不遇时警告! 分数需再压低一档')
    fin_score -= 3

if fin_score >= 6:
    fin_trend = '强烈看涨'
elif fin_score >= 3:
    fin_trend = '偏强看涨'
elif fin_score >= 1:
    fin_trend = '震荡偏强'
elif fin_score >= -2:
    fin_trend = '震荡'
elif fin_score >= -5:
    fin_trend = '偏弱看跌'
else:
    fin_trend = '看跌'

print(f'\n大盘通用趋势: 【{trend}】')
print(f'金融期货专项趋势: 【{fin_trend}】(评分: {fin_score})')
print()

print('─' * 80)
print('分析信号汇总:')
for s in signals:
    print(f'  {s}')
if is_wby:
    print(f'  [!!] 五不遇时: {wby_msg}')
print()

print('═' * 80)
print('【结论】金融期货（股指 IH/IF/IC/IM）夜盘走势研判')
print('═' * 80)

# 核心结论
fire_summary = []
if fire_palace not in ci['kong_palaces']:
    if f_door in ['景门', '开门', '生门']:
        fire_summary.append('火宫景气，市场情绪积极')
    elif f_door in ['死门']:
        fire_summary.append('火宫死门，热度低迷')
else:
    fire_summary.append('火宫逢空，多头缺乏持续动力')

gold_summary = []
for gp in [6, 7]:
    if gp not in ci['kong_palaces']:
        gd = doors.get(gp, '')
        if gd in ['开门', '生门']:
            gold_summary.append(f'{gp}宫(金)临{gd}，资金面良好')

if not gold_summary:
    gold_summary.append('金宫无明显利好，资金偏谨慎')

for s in fire_summary:
    print(f'  火(热度): {s}')
for s in gold_summary:
    print(f'  金(资金): {s}')

print()
print(f'  综合判断: {fin_trend}')
print(f'  操作建议: ', end='')
if '看涨' in fin_trend:
    print('可谨慎做多，关注22:30-23:00时段的马星异动')
elif '震荡' in fin_trend:
    print('建议观望或轻仓高抛低吸')
else:
    print('建议观望或轻仓做空')

print('=' * 80)
