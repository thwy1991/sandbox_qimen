# -*- coding: utf-8 -*-
"""明日（6月8日周一）奇门期货交易分析"""
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate_qimen_image import get_all_gz, get_bureau_info
from qimen_engine_v2 import solve

sessions = [
    (9, 30, '巳时', '早盘 09:30-11:30'),
    (13, 0, '未时', '午盘 13:00-15:00'),
]

GAN_YIN = {'甲':'阳','丙':'阳','戊':'阳','庚':'阳','壬':'阳',
           '乙':'阴','丁':'阴','己':'阴','辛':'阴','癸':'阴'}
GAN_WX  = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土',
           '己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
WX_KE   = {'木':'土','土':'水','水':'火','火':'金','金':'木'}

def is_wu_bu_yu(day_gan, hour_gan):
    dy = GAN_YIN.get(day_gan,''); hy = GAN_YIN.get(hour_gan,'')
    dw = GAN_WX.get(day_gan,''); hw = GAN_WX.get(hour_gan,'')
    return dy == hy and WX_KE.get(hw) == dw

JI_MEN = {'生门', '开门', '休门'}
XIONG_MEN = {'死门', '惊门', '伤门'}
JI_SHEN = {'值符', '九天', '六合'}
XIONG_SHEN = {'白虎', '玄武'}

print('='*70)
print('2026年6月8日 周一 A股/期货交易时段 奇门分析')
print('='*70)

for h,m,zhi,session_name in sessions:
    dt = datetime(2026, 6, 8, h, m)
    ygz, mgz, dgz, hgz = get_all_gz(dt)
    jq, dun, bureau, yuan = get_bureau_info(dt)
    result = solve(ygz, mgz, dgz, hgz, jq, dun, bureau)
    ci = result['chart_info']
    dp = result['di_pan']
    hv = result['hv_stems']
    hs = result['hv_stars']
    pd_doors = result['palace_doors']
    pg = result['palace_gods']
    kong = ci['kong_palaces']
    ma_p = ci['ma_palace']

    # 五不遇时
    wubu = is_wu_bu_yu(dgz[0], hgz[0])

    # 时干落宫
    hour_gan_pos = next((p for p,g in dp.items() if g == hgz[0]), 1)
    # 日干落宫
    day_gan_pos = next((p for p,g in dp.items() if g == dgz[0]), 1)
    # 天盘戊
    wu_pos = next((p for p,g in hv.items() if g == '戊'), 1)
    # 生门/开门
    sm_pos = next((p for p,d in pd_doors.items() if d == '生门'), None)
    km_pos = next((p for p,d in pd_doors.items() if d == '开门'), None)

    zf_pos = ci['zhi_fu_heaven_pos']
    zs_pos = ci['zhi_shi_pos']

    print(f'\n--- {session_name} | 四柱: {ygz} {mgz} {dgz} {hgz} ---')
    print(f'节气: {jq}{yuan} {dun}遁{bureau}局 | 值符: {ci["zhi_fu_star"]}落{zf_pos}宫 | 值使: {ci["zhi_shi_door"]}落{zs_pos}宫')
    print(f'旬空: {ci["kong_pair"]} -> {kong} | 马星: {ci["ma_zhi"]} -> {ma_p}宫')

    if wubu:
        print(f'!!! 【五不遇时】{dgz[0]}(日干)遇{hgz[0]}(时干) - 大凶时辰！！！')
    else:
        print(f'OK 非五不遇时 ({dgz[0]}日 {hgz[0]}时)')

    signals = []

    # 维度1: 时干宫
    h_door = pd_doors.get(hour_gan_pos, '')
    h_kong = hour_gan_pos in kong
    print(f'\n  [时干宫{hour_gan_pos}] {pg.get(hour_gan_pos,"")}|{hs.get(hour_gan_pos,"")}|天盘{hv.get(hour_gan_pos,"")}|{h_door}|地盘{dp.get(hour_gan_pos,"")} {"[空]" if h_kong else ""}')
    if pg.get(hour_gan_pos,'') in XIONG_SHEN: print(f'    [!] 时干临凶神 {pg[hour_gan_pos]}'); signals.append(-1)
    if pg.get(hour_gan_pos,'') in JI_SHEN: print(f'    [+] 时干临吉神 {pg[hour_gan_pos]}'); signals.append(1)
    if h_door in XIONG_MEN: print(f'    [!] 时干临凶门 {h_door}'); signals.append(-1)
    if h_door in JI_MEN: print(f'    [+] 时干临吉门 {h_door}'); signals.append(1)
    if h_kong: print(f'    [!] 时干宫逢空亡'); signals.append(-1)

    # 维度2: 值符宫
    zf_kong = zf_pos in kong
    print(f'  [值符宫{zf_pos}] {pg.get(zf_pos,"")}|{pd_doors.get(zf_pos,"")} {"[空]" if zf_kong else ""}')
    if zf_kong: print(f'    [!] 值符逢空亡'); signals.append(-1)
    if pd_doors.get(zf_pos,'') in XIONG_MEN: print(f'    [!] 值符临凶门 {pd_doors[zf_pos]}'); signals.append(-1)
    if pd_doors.get(zf_pos,'') in JI_MEN: print(f'    [+] 值符临吉门 {pd_doors[zf_pos]}'); signals.append(1)

    # 维度3: 资金戊
    wu_kong = wu_pos in kong
    print(f'  [天盘戊(资金)宫{wu_pos}] {pg.get(wu_pos,"")}|{pd_doors.get(wu_pos,"")} {"[空]" if wu_kong else ""}')
    if wu_kong: print(f'    [!] 资金宫逢空亡'); signals.append(-1)
    if pd_doors.get(wu_pos,'') in XIONG_MEN: print(f'    [!] 资金临凶门 {pd_doors[wu_pos]}'); signals.append(-1)
    if pd_doors.get(wu_pos,'') in JI_MEN: print(f'    [+] 资金临吉门 {pd_doors[wu_pos]}'); signals.append(1)

    # 维度4: 生门
    if sm_pos:
        sm_kong = sm_pos in kong
        ji_xing = {'天心','天辅','天禽'}
        print(f'  [生门宫{sm_pos}] {pg.get(sm_pos,"")}|{hs.get(sm_pos,"")}|{hv.get(sm_pos,"")}|{dp.get(sm_pos,"")} {"[空]" if sm_kong else ""}')
        if sm_kong: print(f'    [!] 生门逢空亡'); signals.append(-1)
        if pg.get(sm_pos,'') in XIONG_SHEN: print(f'    [!] 生门临凶神 {pg[sm_pos]}'); signals.append(-1)
        if hs.get(sm_pos,'') in ji_xing: print(f'    [+] 生门得吉星 {hs[sm_pos]}'); signals.append(1)

    # 维度5: 开门
    if km_pos and km_pos != 5:
        km_kong = km_pos in kong
        print(f'  [开门宫{km_pos}] {pg.get(km_pos,"")}|{hs.get(km_pos,"")}|{hv.get(km_pos,"")} {"[空]" if km_kong else ""}')
        if km_kong: print(f'    [!] 开门逢空亡'); signals.append(-1)
        if pg.get(km_pos,'') in JI_SHEN: print(f'    [+] 开门得吉神 {pg[km_pos]}'); signals.append(1)

    # 维度6: 马星
    ma_god = pg.get(ma_p, '')
    ma_door = pd_doors.get(ma_p, '')
    print(f'  [马星宫{ma_p}] {ma_god}|{ma_door}')
    if ma_god == '九天': print(f'    [+] 马星临九天'); signals.append(1)
    if ma_god == '九地': print(f'    [!] 马星临九地'); signals.append(-1)
    if ma_door in XIONG_MEN: print(f'    [!] 马星临凶门 {ma_door}'); signals.append(-1)

    # 维度7: 日干宫
    r_kong = day_gan_pos in kong
    print(f'  [日干宫{day_gan_pos}] {pg.get(day_gan_pos,"")}|{pd_doors.get(day_gan_pos,"")} {"[空]" if r_kong else ""}')
    if r_kong: print(f'    [!] 日干逢空亡'); signals.append(-1)
    if pd_doors.get(day_gan_pos,'') in JI_MEN: print(f'    [+] 日干临吉门 {pd_doors[day_gan_pos]}'); signals.append(1)

    # 综合评分
    neg_weighted = sum(abs(s) for s in signals if s < 0)
    if wubu:
        neg_weighted += 3

    pos_count = sum(1 for s in signals if s > 0)

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
    print(f'  >> 信号: {signals}')

print('\n' + '='*70)
print('免责: 以上基于奇门遁甲模型，仅供参考研究，不构成投资建议。')
