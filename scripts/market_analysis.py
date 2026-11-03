# -*- coding: utf-8 -*-
"""
A股交易时段奇门遁甲大盘分析脚本
分析期间：2026年6月8日 - 6月12日，每个交易日两个时段
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generate_qimen_image import get_all_gz, get_bureau_info
from qimen_engine_v2 import solve, PALACE_DIZHI, DIZHI_TO_PALACE

# ── 五行对照 ─────────────────────────────────────────────────
WUXING = {
    1:'水', 2:'土', 3:'木', 4:'木',
    5:'土', 6:'金', 7:'金', 8:'土', 9:'火'
}

PALACE_GUA = {
    1:'坎⚍', 2:'坤☷', 3:'震☳', 4:'巽☴',
    5:'中', 6:'乾☰', 7:'兑☱', 8:'艮☶', 9:'离☲'
}

# 天干五行
GAN_WX = {
    '甲':'木','乙':'木','丙':'火','丁':'火','戊':'土',
    '己':'土','庚':'金','辛':'金','壬':'水','癸':'水'
}

# 天干阴阳
GAN_YIN = {
    '甲':'阳','丙':'阳','戊':'阳','庚':'阳','壬':'阳',
    '乙':'阴','丁':'阴','己':'阴','辛':'阴','癸':'阴'
}

# 五行相克：key克value
WX_KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}

# 八门含义（股市相关）
DOOR_MEANING = {
    '休门': '休养生息/观望',
    '生门': '生机财利/上涨',
    '伤门': '损伤破败/下跌',
    '杜门': '杜塞阻滞/横盘',
    '景门': '景气象/活跃',
    '死门': '死气沉沉/低迷',
    '惊门': '惊恐动荡/震荡',
    '开门': '开畅通达/上扬',
}

# 八神含义（股市相关）
GOD_MEANING = {
    '值符': '主导力量/趋势明确',
    '腾蛇': '虚浮不定/假象',
    '太阴': '暗中蓄力/阴跌',
    '六合': '聚合和谐/平稳',
    '白虎': '凶猛杀伤/暴跌',
    '玄武': '暗昧盗耗/阴跌',
    '九地': '低迷固守/底部',
    '九天': '高扬上升/上涨',
}

def get_key_palace_info(result):
    """提取关键宫位信息用于股市分析"""
    ci = result['chart_info']
    dp = result['di_pan']
    hv = result['hv_stems']
    doors = result['palace_doors']
    gods = result['palace_gods']
    earth_gods = result['earth_gods']
    stars = result['hv_stars']
    
    hour_gan = ci['time'].split('日')[1].strip()[0] if '日' in ci['time'] else ''
    day_gan = ci['time'].split('月')[1].strip()[0] if '月' in ci['time'] else ''
    
    # 找出关键干的位置
    hour_gan_pos = None
    for p, g in dp.items():
        if g == hour_gan:
            hour_gan_pos = p
            break
    
    # 找日干在地盘的位置
    day_gan_pos = None
    for p, g in dp.items():
        if g == day_gan:
            day_gan_pos = p
            break
    
    # 找戊（资金）在天盘的位置
    wu_pos = None
    for p, g in hv.items():
        if g == '戊':
            wu_pos = p
            break
    
    # 找生门、开门位置
    sheng_pos = None
    kai_pos = None
    for p, d in doors.items():
        if d == '生门':
            sheng_pos = p
        if d == '开门':
            kai_pos = p
    
    return {
        'hour_gan': hour_gan, 'hour_gan_pos': hour_gan_pos,
        'day_gan': day_gan, 'day_gan_pos': day_gan_pos,
        'wu_pos': wu_pos,
        'sheng_pos': sheng_pos,
        'kai_pos': kai_pos,
    }


def is_wu_bu_yu_shi(day_gan, hour_gan):
    """判断是否为五不遇时：时干克日干且同性相克（阳克阳/阴克阴），大凶"""
    if not day_gan or not hour_gan:
        return False, ''
    day_wx = GAN_WX.get(day_gan, '')
    hour_wx = GAN_WX.get(hour_gan, '')
    day_yin = GAN_YIN.get(day_gan, '')
    hour_yin = GAN_YIN.get(hour_gan, '')
    if day_yin == hour_yin and WX_KE.get(hour_wx) == day_wx:
        msg = (f'[!!]五不遇时：{day_gan}({day_yin}{day_wx})日{hour_gan}({hour_yin}{hour_wx})时，'
               f'时干克日干且同性相克，大凶之兆')
        return True, msg
    return False, ''


def analyze_market(result):
    """基于奇门盘面分析股市走势"""
    ci = result['chart_info']
    info = get_key_palace_info(result)
    hp = info['hour_gan_pos']
    dp_pos = info['day_gan_pos']
    wu = info['wu_pos']
    sheng = info['sheng_pos']
    kai = info['kai_pos']
    hour_gan = info['hour_gan']
    day_gan = info['day_gan']
    
    gods = result['palace_gods']
    earth_gods = result['earth_gods']
    stars = result['hv_stars']
    doors = result['palace_doors']
    dp = result['di_pan']
    hv = result['hv_stems']
    
    dun = ci['dun']
    zf_h_pos = ci['zhi_fu_heaven_pos']
    zs_pos = ci['zhi_shi_pos']
    kong = ci['kong_palaces']
    ma = ci['ma_palace']
    
    signals = []
    trend = '震荡'
    
    # 0. 五不遇时检查（时辰格局，优先检测，大凶之兆）
    is_wby, wby_msg = is_wu_bu_yu_shi(day_gan, hour_gan)
    if is_wby:
        signals.append(wby_msg)  # 以[!!]标识，权重3倍
    
    # 1. 时干宫分析（事体）
    if hp:
        h_wx = WUXING[hp]
        h_god = gods.get(hp, '')
        h_star = stars.get(hp, '')
        h_door = doors.get(hp, '')
        
        if h_god in ['九天', '值符', '六合']:
            signals.append(f'时干宫({hp})吉神{h_god}')
        elif h_god in ['白虎', '玄武']:
            signals.append(f'[!]时干宫({hp})凶神{h_god}')
        
        if h_door in ['生门', '开门', '休门']:
            signals.append(f'时干宫({hp})吉门{h_door}')
        elif h_door in ['死门', '惊门', '伤门']:
            signals.append(f'[!]时干宫({hp})凶门{h_door}')
        
        if hp in kong:
            signals.append(f'[!]时干宫({hp})逢空亡，能量减弱')
    
    # 2. 值符宫分析（趋势主导）
    zf_god = gods.get(zf_h_pos, '')
    zf_door = doors.get(zf_h_pos, '')
    if zf_h_pos in kong:
        signals.append(f'[!]值符宫({zf_h_pos})逢空，主力虚浮')
    else:
        if zf_door in ['生门', '开门']:
            signals.append(f'值符宫({zf_h_pos}){zf_door}，主力积极')
        elif zf_door in ['死门', '惊门']:
            signals.append(f'[!]值符宫({zf_h_pos}){zf_door}，主力退缩')
    
    # 3. 资金宫（天盘戊）
    if wu:
        wu_wx = WUXING[wu]
        wu_star = stars.get(wu, '')
        wu_door = doors.get(wu, '')
        if wu in kong:
            signals.append(f'[!]资金宫({wu})戊逢空亡，资金不足')
        else:
            if wu_door in ['生门', '开门']:
                signals.append(f'资金宫({wu}){wu_door}，资金面利好')
    
    # 4. 生门/开门分析
    if sheng and sheng not in kong:
        sheng_wx = WUXING[sheng]
        sheng_star = stars.get(sheng, '')
        if sheng_star in ['天心', '天辅', '天禽']:
            signals.append(f'生门({sheng})得吉星{sheng_star}')
    if sheng and sheng in kong:
        signals.append(f'[!]生门({sheng})逢空，生机不足')
    
    # 5. 马星分析（波动）
    if ma:
        ma_wx = WUXING[ma]
        ma_door = doors.get(ma, '')
        ma_god = gods.get(ma, '')
        if ma_god in ['九天']:
            signals.append(f'马星({ma})临九天，快速拉升')
        elif ma_god in ['九地']:
            signals.append(f'马星({ma})临九地，冲高回落')
        elif ma_door in ['伤门', '惊门']:
            signals.append(f'[!]马星({ma})临{ma_door}，剧烈波动')
    
    # 6. 日干宫（大盘主体）
    if dp_pos:
        d_wx = WUXING[dp_pos]
        d_door = doors.get(dp_pos, '')
        d_god = gods.get(dp_pos, '')
        if dp_pos in kong:
            signals.append(f'[!]日干宫({dp_pos})逢空，大盘无力')
        if d_door in ['开门', '生门']:
            signals.append(f'日干({dp_pos}){d_door}，大盘向好')
    
    # 综合判断
    # [!!] = 五不遇时大凶，计3个警告；[!] = 普通利空，计1个警告
    wby_count = sum(1 for s in signals if s.startswith('[!!]'))
    regular_bad = sum(1 for s in signals if s.startswith('[!]') and not s.startswith('[!!]'))
    warning_count = wby_count * 3 + regular_bad
    
    if warning_count == 0:
        trend = '看涨'
    elif warning_count <= 2:
        trend = '偏多'
    elif warning_count <= 3:
        trend = '震荡'
    elif warning_count <= 5:
        trend = '偏空'
    else:
        trend = '看跌'
    
    return trend, signals


def generate_all_analyses():
    """生成6月8日至12日所有交易时段的奇门分析"""
    
    days = range(8, 13)  # 6月8日-12日
    sessions = [
        (9, 30, '巳', '早盘'),
        (13, 0, '未', '午盘'),
    ]
    
    results = []
    
    for day in days:
        for h, m, zhi_name, session_name in sessions:
            dt = datetime(2026, 6, day, h, m)
            
            year_gz, month_gz, day_gz, hour_gz = get_all_gz(dt)
            jieqi_name, dun, bureau_num, yuan = get_bureau_info(dt)
            result = solve(year_gz, month_gz, day_gz, hour_gz, jieqi_name, dun, bureau_num)
            
            ci = result['chart_info']
            trend, signals = analyze_market(result)
            
            doors = result['palace_doors']
            gods = result['palace_gods']
            hv = result['hv_stems']
            stars = result['hv_stars']
            
            weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            weekday = weekdays[dt.weekday()]
            
            # 提取关键信息
            info = get_key_palace_info(result)
            
            # 生门、开门信息
            sheng_info = ''
            for p, d in doors.items():
                if d == '生门':
                    s_god = gods.get(p, '')
                    s_star = stars.get(p, '')
                    s_wx = WUXING[p]
                    sheng_info = f'{p}宫({s_wx}) {s_star} {s_god}'
            
            kai_info = ''
            for p, d in doors.items():
                if d == '开门':
                    k_god = gods.get(p, '')
                    k_star = stars.get(p, '')
                    k_wx = WUXING[p]
                    kai_info = f'{p}宫({k_wx}) {k_star} {k_god}'
            
            # 值符宫信息
            zf_hp = ci['zhi_fu_heaven_pos']
            zf_god_h = gods.get(zf_hp, '')
            zf_door_h = doors.get(zf_hp, '')
            
            # 检测五不遇时
            wby_flag = '五不遇时' if is_wu_bu_yu_shi(info['day_gan'], info['hour_gan'])[0] else '--'
            
            results.append({
                'date': f'6/{day}',
                'weekday': weekday,
                'session': session_name,
                'time': f'{h:02d}:{m:02d}',
                'hour_gz': hour_gz,
                'day_gz': day_gz,
                'bureau': f'{dun}遁{bureau_num}局',
                'yuan': yuan,
                'jieqi': jieqi_name,
                'zhi_fu_star': ci['zhi_fu_star'],
                'zhi_fu_pos': f'{zf_hp}宫 {zf_god_h} {zf_door_h}',
                'zhi_shi_pos': f'{ci["zhi_shi_pos"]}宫 {ci["zhi_shi_door"]}',
                'kong': f'{ci["kong_pair"]} → {ci["kong_palaces"]}宫',
                'ma': f'{ci["ma_zhi"]}({ci["ma_palace"]}宫)',
                'sheng_men': sheng_info,
                'kai_men': kai_info,
                'wu_pos': f'{info["wu_pos"]}宫' if info["wu_pos"] else '--',
                'trend': trend,
                'wubuyushi': wby_flag,
                'signals': signals,
                'hour_gan_pos': info['hour_gan_pos'],
                'day_gan_pos': info['day_gan_pos'],
            })
    
    return results


def print_table(results):
    """打印分析表格"""
    print('\n' + '=' * 140)
    print('                     A股交易时段奇门遁甲分析表（2026年6月8日 - 12日）')
    print('=' * 140)
    
    for r in results:
        print(f'\n{"─" * 140}')
        print(f'【{r["date"]} {r["weekday"]} {r["session"]} {r["time"]}】'
              f' 四柱日时: {r["day_gz"]} {r["hour_gz"]}  |  {r["bureau"]}({r["yuan"]}) {r["jieqi"]}')
        wby_line = f'  *** 五不遇时! ***' if r['wubuyushi'] != '--' else ''
        print(f'  局数: {r["bureau"]}  |  值符: {r["zhi_fu_star"]} → {r["zhi_fu_pos"]}  |  值使: {r["zhi_shi_pos"]}{wby_line}')
        print(f'  旬空: {r["kong"]}  |  马星: {r["ma"]}')
        print(f'  生门: {r["sheng_men"]}  |  开门: {r["kai_men"]}  |  天盘戊: {r["wu_pos"]}')
        print(f'  趋势判断: 【{r["trend"]}】')
        for s in r['signals']:
            print(f'    → {s}')
    
    print(f'\n{"=" * 140}\n')


def generate_markdown_table(results):
    """生成Markdown格式的分析表格"""
    md = []
    md.append('# A股交易时段奇门遁甲分析报告')
    md.append(f'\n> 分析期间：2026年6月8日（周一）至 6月12日（周五）')
    md.append('> 交易时段：早盘 9:30（巳时）/ 午盘 13:00（未时）\n')
    
    md.append('## 一、盘面总览\n')
    md.append('| 日期 | 星期 | 时段 | 四柱(日/时) | 局数 | 五不遇时 | 值符 | 值使 | 旬空 | 马星 | 生门 | 开门 | 天盘戊 | 趋势 |')
    md.append('|------|------|------|------------|------|----------|------|------|------|------|------|------|--------|------|')
    
    for r in results:
        wby_display = '**' + r['wubuyushi'] + '**' if r['wubuyushi'] != '--' else '--'
        md.append(f'| {r["date"]} | {r["weekday"]} | {r["session"]} | {r["day_gz"]}/{r["hour_gz"]} | '
                  f'{r["bureau"]} | {wby_display} | {r["zhi_fu_star"]}→{r["zhi_fu_pos"]} | {r["zhi_shi_pos"]} | '
                  f'{r["kong"]} | {r["ma"]} | {r["sheng_men"]} | {r["kai_men"]} | {r["wu_pos"]} | '
                  f'**{r["trend"]}** |')
    
    md.append('\n## 二、各时段详细分析\n')
    
    for r in results:
        md.append(f'### {r["date"]} {r["weekday"]} {r["session"]} {r["time"]}\n')
        md.append(f'- **四柱日时**: {r["day_gz"]} {r["hour_gz"]}')
        md.append(f'- **五不遇时**: {r["wubuyushi"]}')
        md.append(f'- **局数**: {r["bureau"]}({r["yuan"]}) {r["jieqi"]}')
        md.append(f'- **值符**: {r["zhi_fu_star"]} → {r["zhi_fu_pos"]}')
        md.append(f'- **值使**: {r["zhi_shi_pos"]}')
        md.append(f'- **旬空**: {r["kong"]}')
        md.append(f'- **马星**: {r["ma"]}')
        md.append(f'- **生门落宫**: {r["sheng_men"]}')
        md.append(f'- **开门落宫**: {r["kai_men"]}')
        md.append(f'- **天盘戊（资金）**: {r["wu_pos"]}')
        md.append(f'- **趋势判断**: **{r["trend"]}**')
        md.append(f'\n**分析要点**:')
        for s in r['signals']:
            md.append(f'- {s}')
        md.append('')
    
    md.append('\n## 三、一周趋势总览\n')
    md.append('| 日期 | 早盘趋势 | 午盘趋势 |')
    md.append('|------|----------|----------|')
    
    for day in range(8, 13):
        day_results = [r for r in results if r['date'] == f'6/{day}']
        morning = day_results[0]['trend'] if len(day_results) > 0 else '--'
        afternoon = day_results[1]['trend'] if len(day_results) > 1 else '--'
        weekdays_map = {8:'周一',9:'周二',10:'周三',11:'周四',12:'周五'}
        md.append(f'| 6/{day} {weekdays_map[day]} | {morning} | {afternoon} |')
    
    md.append('\n---')
    md.append(f'\n*本报告由奇门遁甲排盘引擎自动生成，仅供参考，不构成投资建议。*')
    
    return '\n'.join(md)


if __name__ == '__main__':
    results = generate_all_analyses()
    print_table(results)
    
    # 生成Markdown报告
    md_content = generate_markdown_table(results)
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs')
    os.makedirs(docs_dir, exist_ok=True)
    md_path = os.path.join(docs_dir, 'A股交易时段奇门分析_0608_0612.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f'\nMarkdown报告已保存: {md_path}')
