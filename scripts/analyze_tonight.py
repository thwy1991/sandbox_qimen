# -*- coding: utf-8 -*-
"""今晚(6月8日) 21:20 亥时 奇门排盘 + 金属期货多头分析"""
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate_qimen_image import get_all_gz, get_bureau_info
from qimen_engine_v2 import solve

# ── 6月8日 21:20 亥时 ──
dt = datetime(2026, 6, 8, 21, 20)
ygz, mgz, dgz, hgz = get_all_gz(dt)
jq, dun, bureau, yuan = get_bureau_info(dt)
result = solve(ygz, mgz, dgz, hgz, jq, dun, bureau)
ci = result['chart_info']
dp = result['di_pan']           # 地盘干 {宫:干}
hv = result['hv_stems']         # 天盘干 {宫:干}
hs = result['hv_stars']         # 天盘星 {宫:星}
pd_doors = result['palace_doors']  # 八门 {宫:门}
pg = result['palace_gods']      # 八神 {宫:神}
kong = ci['kong_palaces']       # 空亡宫列表
ma_p = ci['ma_palace']          # 马星宫

# ── 辅助函数 ──
GAN_YIN = {'甲':'阳','丙':'阳','戊':'阳','庚':'阳','壬':'阳',
           '乙':'阴','丁':'阴','己':'阴','辛':'阴','癸':'阴'}
GAN_WX  = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土',
           '己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
WX_KE   = {'木':'土','土':'水','水':'火','火':'金','金':'木'}

JI_MEN = {'生门','开门','休门'}
XIONG_MEN = {'死门','惊门','伤门'}
JI_SHEN = {'值符','九天','六合'}
XIONG_SHEN = {'白虎','玄武'}

def is_wu_bu_yu(day_gan, hour_gan):
    dy = GAN_YIN.get(day_gan,''); hy = GAN_YIN.get(hour_gan,'')
    dw = GAN_WX.get(day_gan,''); hw = GAN_WX.get(hour_gan,'')
    return dy == hy and WX_KE.get(hw) == dw

# ── 宫位五行 ──
PALACE_WX = {1:'水', 2:'土', 3:'木', 4:'木', 5:'土', 6:'金', 7:'金', 8:'土', 9:'火'}

# ── 基本盘面 ──
print('='*70)
print('  奇门遁甲排盘 -- 2026年6月8日 21:20 (亥时)')
print('='*70)
print(f'四柱: {ygz} {mgz} {dgz} {hgz}')
print(f'节气: {jq}{yuan} | {dun}遁{bureau}局')
print(f'旬首: {ci["xun_shou_gan"]} | 值符: {ci["zhi_fu_star"]} 落 {ci["zhi_fu_heaven_pos"]}宫 | 值使: {ci["zhi_shi_door"]} 落 {ci["zhi_shi_pos"]}宫')
print(f'旬空: {ci["kong_pair"]} -> {kong} | 马星: {ci["ma_zhi"]} -> {ma_p}宫')

LEN = {1:'坎一', 2:'坤二', 3:'震三', 4:'巽四', 5:'中五', 6:'乾六', 7:'兑七', 8:'艮八', 9:'离九'}

print(f'\n{"━"*60}')
# 九宫表格
lines = [[4,9,2],[3,5,7],[8,1,6]]
for row in lines:
    for p in row:
        if p == 5:
            s = f'[中五宫] 地盘:{dp.get(5,"?")}'
            print(f'  {s:<55}')
        else:
            mark = ''
            if p in kong: mark += ' [空]'
            if p == ma_p: mark += ' [马]'
            g = pg.get(p,'--')
            sname = hs.get(p,'--')
            hv_s = hv.get(p,'?')
            door = pd_doors.get(p,'--')
            dp_s = dp.get(p,'?')
            print(f'  {LEN[p]}宫 | {g:<4}| {sname:<4}| 天{hv_s:<2}| {door:<4}| 地{dp_s:<2}{mark}')

# ── 七维度分析 ──
print(f'\n{"="*70}')
print('  七维度股市分析')
print(f'{"="*70}')

wubu = is_wu_bu_yu(dgz[0], hgz[0])
if wubu:
    print(f'\n  [!!] 五不遇时: {dgz[0]}(日干) 遇 {hgz[0]}(时干) -- 大凶时辰!')
else:
    print(f'\n  [OK] 非五不遇时 ({dgz[0]}日 {hgz[0]}时)')

signals = []
hour_gan_pos = next((p for p,g in dp.items() if g == hgz[0]), 1)
day_gan_pos = next((p for p,g in dp.items() if g == dgz[0]), 1)
wu_pos = next((p for p,g in hv.items() if g == '戊'), 1)
sm_pos = next((p for p,d in pd_doors.items() if d == '生门'), None)
km_pos = next((p for p,d in pd_doors.items() if d == '开门'), None)
zf_pos = ci['zhi_fu_heaven_pos']
zs_pos = ci['zhi_shi_pos']

# 维度1: 时干宫
h_door = pd_doors.get(hour_gan_pos, '')
h_kong = hour_gan_pos in kong
print(f'\n  [时干宫{hour_gan_pos}] {pg.get(hour_gan_pos,"")}|{hs.get(hour_gan_pos,"")}|天{hv.get(hour_gan_pos,"")}|{h_door}|地{dp.get(hour_gan_pos,"")} {"[空]" if h_kong else ""}')
if pg.get(hour_gan_pos,'') in XIONG_SHEN: print(f'    [!] 时干临凶神 {pg[hour_gan_pos]}'); signals.append(-1)
if pg.get(hour_gan_pos,'') in JI_SHEN: print(f'    [+] 时干临吉神 {pg[hour_gan_pos]}'); signals.append(1)
if h_door in XIONG_MEN: print(f'    [!] 时干临凶门 {h_door}'); signals.append(-1)
if h_door in JI_MEN: print(f'    [+] 时干临吉门 {h_door}'); signals.append(1)
if h_kong: print(f'    [!] 时干宫逢空亡'); signals.append(-1)

# 维度2: 值符宫
zf_door = pd_doors.get(zf_pos, '')
zf_kong = zf_pos in kong
print(f'  [值符宫{zf_pos}] {pg.get(zf_pos,"")}|{hs.get(zf_pos,"")}|天{hv.get(zf_pos,"")}|{zf_door}|地{dp.get(zf_pos,"")} {"[空]" if zf_kong else ""}')
if zf_kong: print(f'    [!] 值符逢空亡,主力虚浮'); signals.append(-1)
if zf_door in XIONG_MEN: print(f'    [!] 值符临凶门 {zf_door}'); signals.append(-1)
if zf_door in JI_MEN: print(f'    [+] 值符临吉门 {zf_door}'); signals.append(1)

# 维度3: 资金戊
wu_door = pd_doors.get(wu_pos, '')
wu_kong = wu_pos in kong
print(f'  [资金戊(天盘)宫{wu_pos}] {pg.get(wu_pos,"")}|{hs.get(wu_pos,"")}|天{hv.get(wu_pos,"")}|{wu_door}|地{dp.get(wu_pos,"")} {"[空]" if wu_kong else ""}')
if wu_kong: print(f'    [!] 资金宫逢空亡,资金不足'); signals.append(-1)
if wu_door in XIONG_MEN: print(f'    [!] 资金临凶门 {wu_door}'); signals.append(-1)
if wu_door in JI_MEN: print(f'    [+] 资金临吉门 {wu_door}'); signals.append(1)

# 维度4: 生门
if sm_pos:
    sm_kong = sm_pos in kong
    ji_xing = {'天心','天辅','天禽'}
    print(f'  [生门宫{sm_pos}] {pg.get(sm_pos,"")}|{hs.get(sm_pos,"")}|天{hv.get(sm_pos,"")}|地{dp.get(sm_pos,"")} {"[空]" if sm_kong else ""}')
    if sm_kong: print(f'    [!] 生门逢空亡'); signals.append(-1)
    if pg.get(sm_pos,'') in XIONG_SHEN: print(f'    [!] 生门临凶神 {pg[sm_pos]}'); signals.append(-1)
    if hs.get(sm_pos,'') in ji_xing: print(f'    [+] 生门得吉星 {hs[sm_pos]}'); signals.append(1)

# 维度5: 开门
if km_pos and km_pos != 5:
    km_kong = km_pos in kong
    print(f'  [开门宫{km_pos}] {pg.get(km_pos,"")}|{hs.get(km_pos,"")}|天{hv.get(km_pos,"")}|地{dp.get(km_pos,"")} {"[空]" if km_kong else ""}')
    if km_kong: print(f'    [!] 开门逢空亡'); signals.append(-1)
    if pg.get(km_pos,'') in JI_SHEN: print(f'    [+] 开门得吉神 {pg[km_pos]}'); signals.append(1)

# 维度6: 马星
ma_god = pg.get(ma_p, '')
ma_door = pd_doors.get(ma_p, '')
ma_star = hs.get(ma_p, '')
print(f'  [马星宫{ma_p}] {ma_god}|{ma_star}|{ma_door}')
if ma_god == '九天': print(f'    [+] 马星临九天,快速拉升'); signals.append(1)
if ma_god == '九地': print(f'    [!] 马星临九地,冲高回落'); signals.append(-1)
if ma_door in XIONG_MEN: print(f'    [!] 马星临凶门 {ma_door}'); signals.append(-1)
if ma_door in JI_MEN: print(f'    [+] 马星临吉门 {ma_door}'); signals.append(1)

# 维度7: 日干宫
r_door = pd_doors.get(day_gan_pos, '')
r_kong = day_gan_pos in kong
print(f'  [日干宫{day_gan_pos}] {pg.get(day_gan_pos,"")}|{hs.get(day_gan_pos,"")}|天{hv.get(day_gan_pos,"")}|{r_door}|地{dp.get(day_gan_pos,"")} {"[空]" if r_kong else ""}')
if r_kong: print(f'    [!] 日干逢空亡,大盘无力'); signals.append(-1)
if r_door in JI_MEN: print(f'    [+] 日干临吉门 {r_door}'); signals.append(1)

# 综合评分
neg_weighted = sum(abs(s) for s in signals if s < 0)
pos_count = sum(1 for s in signals if s > 0)
if wubu:
    neg_weighted += 3

if neg_weighted == 0:
    trend = '看涨'
elif neg_weighted <= 2:
    trend = '偏多'
elif neg_weighted == 3:
    trend = '震荡'
elif neg_weighted <= 5:
    trend = '偏空'
else:
    trend = '看跌'

print(f'\n  >> 利空加权: {neg_weighted} | 利好信号: {pos_count} | 趋势: {trend}')
print(f'  >> 信号明细: {signals}')

# ══════════════════════════════════════════
# 金属期货(金) 多头 五行专项分析
# ══════════════════════════════════════════
print(f'\n{"="*70}')
print('  金属期货多头 五行专项分析')
print(f'{"="*70}')

print(f'\n  金属 = 金 | 多头需金旺 | 土生金(助) | 火克金(威胁) | 金生水(泄气)')
print(f'  金本宫: 6乾宫(戌亥)、7兑宫(酉)')

print(f'\n  {"─"*55}')
print(f'  {"宫位":<8} {"五行":<6} {"对金":<14} {"八神":<6} {"八门":<6} {"天星":<6} {"标记"}')
print(f'  {"─"*55}')

metal_support = 0
metal_threat = 0

for p in range(1,10):
    wx = PALACE_WX[p]
    if wx == '土':
        rel = '[+]生金'
    elif wx == '金':
        rel = '[*]本宫'
    elif wx == '水':
        rel = '[-]泄金'
    elif wx == '火':
        rel = '[!]克金'
    elif wx == '木':
        rel = '[~]金克木'

    god = pg.get(p, '--')
    door = pd_doors.get(p, '--') if p != 5 else '--'
    star = hs.get(p, '--') if p != 5 else '--'

    status = ''
    if p in kong:
        status += '[空]'
    if p == ma_p:
        status += '[马]'
    if door in JI_MEN:
        status += '[吉门]'
    if god in JI_SHEN:
        status += '[吉神]'
    if god in XIONG_SHEN:
        status += '[凶神]'

    if p == 6 or p == 7:
        if door in JI_MEN and god in JI_SHEN:
            metal_support += 2
        elif door in XIONG_MEN or god in XIONG_SHEN:
            metal_threat += 2
    if wx == '土':
        if door in JI_MEN:
            metal_support += 1
    if wx == '火':
        if god in XIONG_SHEN or door in XIONG_MEN:
            metal_threat += 2
        elif god == '玄武':
            metal_threat += 1

    print(f'  {LEN[p]:<8} {wx:<6} {rel:<14} {god:<6} {door:<6} {star:<6} {status}')

print(f'  {"─"*55}')

# 金属期货特殊宫位分析
print(f'\n  *** 关键宫位细读:')

for p in [6,7]:
    god = pg.get(p,'--')
    door = pd_doors.get(p,'--')
    star = hs.get(p,'--')
    hv_stem = hv.get(p,'?')
    dp_stem = dp.get(p,'?')
    is_kong = p in kong
    print(f'\n  {LEN[p]}宫(金本宫): {god}|{star}|天{hv_stem}|{door}|地{dp_stem}')
    if is_kong: print(f'    [!] 空亡 -- 金气不足!')
    if door == '开门': print(f'    [+] 开门大吉 -- 金属通道顺畅')
    if door in XIONG_MEN: print(f'    [!] {door} -- 金属受压')
    if god == '值符': print(f'    [+] 值符镇守 -- 主力护金')
    if god in XIONG_SHEN: print(f'    [!] {god} -- 干扰金属')
    if god == '九天': print(f'    [+] 九天 -- 有上冲动力')

# 资金戊对金
wu_wx = PALACE_WX[wu_pos]
print(f'\n  资金戊落{LEN[wu_pos]}宫({wu_wx}): ', end='')
if wu_wx == '土':
    print('[+] 土生金,资金面相生金属')
    metal_support += 2
elif wu_wx == '火':
    print('[!] 火克金,资金面压制金属')
    metal_threat += 2
elif wu_wx == '水':
    print('[-] 金生水,资金外流泄金属')
    metal_threat += 1
elif wu_wx == '金':
    print('[+] 资金归金宫,利于金属')
    metal_support += 2
elif wu_wx == '木':
    print('[~] 金克木,金属尚能克制')
    metal_support += 1

# 值符宫对金
zf_wx = PALACE_WX[zf_pos]
print(f'  值符落{LEN[zf_pos]}宫({zf_wx}): ', end='')
if zf_wx == '土':
    print('[+] 土生金,主力支撑金属')
    metal_support += 2
elif zf_wx == '金':
    print('[+] 值符入金宫,主力护盘金属')
    metal_support += 2
elif zf_wx == '水':
    print('[-] 金生水,主力资金外流')
    metal_threat += 1
elif zf_wx == '火':
    print('[!] 火克金,主力打压金属')
    metal_threat += 2

# 生门对金
if sm_pos:
    sm_wx = PALACE_WX[sm_pos]
    print(f'  生门落{LEN[sm_pos]}宫({sm_wx}): ', end='')
    if sm_wx == '土':
        print('[+] 土生金,利润面相生')
        metal_support += 1
    elif sm_wx == '金':
        print('[+] 生门入金宫,利润旺')
        metal_support += 2
    elif sm_wx == '火':
        print('[!] 火克金,利润受损')
        metal_threat += 1

# ── 最终判定 ──
print(f'\n{"="*70}')
print('  *** 金属期货多头 综合判定 ***')
print(f'{"="*70}')

print(f'\n  金属支撑因子: {metal_support}  |  金属威胁因子: {metal_threat}')

if wubu:
    metal_threat += 2

if metal_support >= metal_threat + 3:
    metal_trend = '强烈看涨 -- 金属多头有利'
elif metal_support > metal_threat:
    metal_trend = '偏多 -- 金属多头偏有利'
elif metal_support == metal_threat:
    metal_trend = '震荡 -- 方向不明,谨慎持仓'
elif metal_threat <= metal_support + 2:
    metal_trend = '偏空 -- 金属多头承压'
else:
    metal_trend = '强烈看跌 -- 金属多头危险!'

print(f'  金属走势判定: {metal_trend}')
print(f'  大盘背景: {trend}')

if metal_threat >= 4:
    print(f'\n  [!!!] 风险警告: 威胁因子>=4, 建议严格止损或减仓!')
elif metal_support >= 4:
    print(f'\n  [+++] 强支撑: 支撑因子>=4, 可适量持仓观察')

print(f'\n{"="*70}')
print('  夜盘交易时段: 21:00 - 23:00 (亥时)')
print('  免责: 以上基于奇门遁甲术数模型,仅供研究参考,不构成投资建议。')
print(f'{"="*70}')
