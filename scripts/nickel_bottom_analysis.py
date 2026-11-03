# -*- coding: utf-8 -*-
"""
沪镍底部时间推算 —— 四柱八字+五行旺衰+奇门遁甲 综合分析
分析起点：2026年5月6日（阶段高点）
作者：奇门分析系统
创建日期：2026-06-28
"""
import os
import sys
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generate_qimen_image import get_all_gz, get_bureau_info, get_day_gan_zhi
from qimen_engine_v2 import solve

# ── 五行基础数据 ─────────────────────────────────────────────────
TIANGAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DIZHI   = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

GAN_WX = {
    '甲':'木','乙':'木','丙':'火','丁':'火','戊':'土',
    '己':'土','庚':'金','辛':'金','壬':'水','癸':'水'
}
ZHI_WX = {
    '子':'水','丑':'土','寅':'木','卯':'木',
    '辰':'土','巳':'火','午':'火','未':'土',
    '申':'金','酉':'金','戌':'土','亥':'水'
}
ZHI_HIDDEN = {
    '子': ['癸'],
    '丑': ['己','癸','辛'],
    '寅': ['甲','丙','戊'],
    '卯': ['乙'],
    '辰': ['戊','乙','癸'],
    '巳': ['丙','庚','戊'],
    '午': ['丁','己'],
    '未': ['己','丁','乙'],
    '申': ['庚','壬','戊'],
    '酉': ['辛'],
    '戌': ['戊','辛','丁'],
    '亥': ['壬','甲'],
}

# 宫位五行
PALACE_WX = {1:'水', 2:'土', 3:'木', 4:'木', 5:'土', 6:'金', 7:'金', 8:'土', 9:'火'}

# ── 五运六气 / 月令旺衰 ─────────────────────────────────────────
# 月份地支对应的五行旺衰（十二长生诀用于日干）
TWELVE_STAGE = {
    # 天干在各月令的状态：绝胎养长生沐浴冠带临官帝旺衰病死墓
    # 简化：只看旺(临官/帝旺)、相(长生/冠带)、休、囚、死
}

def get_month_wuxing_strength(month_zhi):
    """根据月令地支，判断各五行当令强弱"""
    mx = ZHI_WX[month_zhi]
    strength = {'金':'囚','木':'休','水':'相','火':'平','土':'平'}
    
    # 月令本位五行最旺
    if mx == '火':
        strength = {'火':'旺','土':'相','金':'死','水':'囚','木':'休'}
    elif mx == '土':
        strength = {'土':'旺','金':'相','水':'死','木':'囚','火':'休'}
    elif mx == '金':
        strength = {'金':'旺','水':'相','木':'死','火':'囚','土':'休'}
    elif mx == '水':
        strength = {'水':'旺','木':'相','火':'死','土':'囚','金':'休'}
    elif mx == '木':
        strength = {'木':'旺','火':'相','土':'死','金':'囚','水':'休'}
    
    return strength

# ── 四柱八字分析 ─────────────────────────────────────────────────
def analyze_bazi(year_gz, month_gz, day_gz, hour_gz=None):
    """分析四柱中五行力量分布"""
    wx_count = {'金':0,'木':0,'水':0,'火':0,'土':0}
    
    for gz in [year_gz, month_gz, day_gz]:
        if len(gz) >= 2:
            g, z = gz[0], gz[1]
            wx_count[GAN_WX[g]] += 1
            wx_count[ZHI_WX[z]] += 1
            # 地支藏干也加权重
            for hg in ZHI_HIDDEN.get(z, []):
                wx_count[GAN_WX[hg]] += 0.5
    
    if hour_gz and len(hour_gz) >= 2:
        g, z = hour_gz[0], hour_gz[1]
        wx_count[GAN_WX[g]] += 1
        wx_count[ZHI_WX[z]] += 1
        for hg in ZHI_HIDDEN.get(z, []):
            wx_count[GAN_WX[hg]] += 0.5
    
    return wx_count


def analyze_qimen_for_date(dt):
    """对指定日期做奇门排盘并提取股市分析关键信号"""
    try:
        year_gz, month_gz, day_gz, hour_gz = get_all_gz(dt)
        jieqi_name, dun, bureau_num, yuan = get_bureau_info(dt)
        result = solve(year_gz, month_gz, day_gz, hour_gz, jieqi_name, dun, bureau_num)
        
        ci = result['chart_info']
        dp = result['di_pan']
        hv = result['hv_stems']
        doors = result['palace_doors']
        gods = result['palace_gods']
        stars = result['hv_stars']
        
        # 找时干落宫
        hour_gan = hour_gz[0]
        hour_pos = None
        for p, g in dp.items():
            if g == hour_gan:
                hour_pos = p
                break
        
        # 找日干落宫
        day_gan = day_gz[0]
        day_pos = None
        for p, g in dp.items():
            if g == day_gan:
                day_pos = p
                break
        
        # 天盘戊（资金）
        wu_pos = None
        for p, g in hv.items():
            if g == '戊':
                wu_pos = p
                break
        
        # 生门、开门
        sheng_pos = None
        kai_pos = None
        for p, d in doors.items():
            if d == '生门':
                sheng_pos = p
            if d == '开门':
                kai_pos = p
        
        kong = ci['kong_palaces']
        ma = ci['ma_palace']
        
        # ── 信号收集 ──
        bullish = []
        bearish = []
        
        # 时干宫
        if hour_pos:
            h_god = gods.get(hour_pos, '')
            h_door = doors.get(hour_pos, '')
            h_wx = PALACE_WX.get(hour_pos, '')
            if h_god in ('值符','九天','六合'):
                bullish.append(f'时干宫({hour_pos})吉神{h_god}')
            if h_god in ('白虎','玄武'):
                bearish.append(f'时干宫({hour_pos})凶神{h_god}')
            if h_door in ('生门','开门','休门'):
                bullish.append(f'时干宫({hour_pos})吉门{h_door}')
            if h_door in ('死门','惊门','伤门'):
                bearish.append(f'时干宫({hour_pos})凶门{h_door}')
            if hour_pos in kong:
                bearish.append(f'时干宫({hour_pos})逢空亡')
        
        # 五不遇时检查
        day_wx = GAN_WX.get(day_gan, '')
        hour_wx = GAN_WX.get(hour_gan, '')
        WX_KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
        GAN_YIN = {'甲':'阳','丙':'阳','戊':'阳','庚':'阳','壬':'阳',
                   '乙':'阴','丁':'阴','己':'阴','辛':'阴','癸':'阴'}
        if (GAN_YIN.get(day_gan) == GAN_YIN.get(hour_gan)
            and WX_KE.get(hour_wx) == day_wx):
            bearish.append(f'!!!五不遇时!!! {day_gan}日{hour_gan}时')
        
        # 值符宫
        zf_pos = ci['zhi_fu_heaven_pos']
        if zf_pos in kong:
            bearish.append(f'值符宫({zf_pos})逢空')
        zf_door = doors.get(zf_pos, '')
        if zf_door in ('生门','开门'):
            bullish.append(f'值符宫({zf_pos}){zf_door}')
        
        # 资金宫
        if wu_pos:
            if wu_pos in kong:
                bearish.append(f'资金宫({wu_pos})戊逢空')
            wu_door = doors.get(wu_pos, '')
            if wu_door in ('生门','开门'):
                bullish.append(f'资金宫({wu_pos}){wu_door}')
        
        # 生门
        if sheng_pos:
            if sheng_pos in kong:
                bearish.append(f'生门({sheng_pos})逢空')
            sheng_star = stars.get(sheng_pos, '')
            sheng_god = gods.get(sheng_pos, '')
            if sheng_star in ('天心','天辅','天禽'):
                bullish.append(f'生门({sheng_pos})吉星{sheng_star}')
            sheng_wx = PALACE_WX.get(sheng_pos, '')
            if sheng_wx == '金':
                bullish.append(f'生门落金宫({sheng_pos})★金气生发★')
        
        # 开门
        if kai_pos:
            kai_wx = PALACE_WX.get(kai_pos, '')
            if kai_wx == '金':
                bullish.append(f'开门落金宫({kai_pos})★金门得位★')
        
        # 日干宫
        if day_pos:
            if day_pos in kong:
                bearish.append(f'日干宫({day_pos})逢空')
            day_door = doors.get(day_pos, '')
            if day_door in ('开门','生门'):
                bullish.append(f'日干宫({day_pos}){day_door}')
        
        # 马星
        if ma:
            ma_god = gods.get(ma, '')
            if ma_god == '九天':
                bullish.append(f'马星临九天')
            elif ma_god == '九地':
                bearish.append(f'马星临九地,可能见底')
        
        # 综合评级
        bs = len(bearish)
        bu = len(bullish)
        
        if bs == 0 and bu >= 3:
            trend = '★★★强看涨'
        elif bs <= 1 and bu >= 2:
            trend = '★★偏多'
        elif bs <= 2 and bu >= 1:
            trend = '★偏多/筑底'
        elif bs >= 3 and bu <= 1:
            trend = '▼偏空'
        elif bs >= 4:
            trend = '▼▼强看跌'
        else:
            trend = '→震荡'
        
        return {
            'dt': dt,
            'hour_gz': hour_gz,
            'day_gz': day_gz,
            'month_gz': month_gz,
            'jieqi': jieqi_name,
            'dun': dun,
            'bureau': bureau_num,
            'yuan': yuan,
            'zf_star': ci['zhi_fu_star'],
            'zf_pos': zf_pos,
            'kong': kong,
            'ma_palace': ma,
            'ma_zhi': ci.get('ma_zhi',''),
            'sheng_pos': sheng_pos,
            'kai_pos': kai_pos,
            'wu_pos': wu_pos,
            'hour_pos': hour_pos,
            'day_pos': day_pos,
            'bullish': bullish,
            'bearish': bearish,
            'trend': trend,
            'trend_score': bu - bs,
        }
    except Exception as e:
        return {'dt': dt, 'error': str(e), 'trend': 'ERROR'}


def print_bazi_analysis(title, dt):
    """打印八字分析"""
    year_gz, month_gz, day_gz, hour_gz = get_all_gz(dt)
    wx = analyze_bazi(year_gz, month_gz, day_gz, hour_gz)
    
    print(f'\n{"="*70}')
    print(f'  {title}  【{dt.strftime("%Y年%m月%d日 %H:%M")}】')
    print(f'{"="*70}')
    print(f'  四柱：年{year_gz} 月{month_gz} 日{day_gz} 时{hour_gz}')
    
    # 五行分析
    total = sum(wx.values())
    print(f'\n  ┌─ 五行力量分布 ─────────────────────────────┐')
    for wx_name in ['金','木','水','火','土']:
        val = wx[wx_name]
        pct = val / total * 100 if total > 0 else 0
        bar = '█' * int(pct / 5)
        status = ''
        if pct > 25:
            status = '← 过旺'
        elif pct < 10:
            status = '← 过弱'
        print(f'  │ {wx_name}: {bar:20s} {pct:5.1f}% {status:10s} │')
    print(f'  └────────────────────────────────────────────┘')
    
    # 日干分析
    day_gan = day_gz[0]
    day_wx = GAN_WX[day_gan]
    
    print(f'\n  ◆ 日干{day_gan}({day_wx})分析：')
    print(f'    年{year_gz[0]}({GAN_WX[year_gz[0]]})年支{year_gz[1]}({ZHI_WX[year_gz[1]]})')
    print(f'    月{month_gz[0]}({GAN_WX[month_gz[0]]})月支{month_gz[1]}({ZHI_WX[month_gz[1]]})')
    
    # 判断日干旺衰
    month_zhi = month_gz[1]
    month_wx = ZHI_WX[month_zhi]
    if month_wx == day_wx:
        print(f'    月令{month_zhi}({month_wx})与日干{day_gan}({day_wx})同五行 → 日干得令')
    elif (day_wx == '金' and month_wx == '土') or \
         (day_wx == '水' and month_wx == '金') or \
         (day_wx == '木' and month_wx == '水') or \
         (day_wx == '火' and month_wx == '木') or \
         (day_wx == '土' and month_wx == '火'):
        print(f'    月令{month_zhi}({month_wx})生助日干{day_gan}({day_wx}) → 日干得生')
    elif (day_wx == '金' and month_wx == '火') or \
         (day_wx == '木' and month_wx == '金') or \
         (day_wx == '土' and month_wx == '木') or \
         (day_wx == '水' and month_wx == '土') or \
         (day_wx == '火' and month_wx == '水'):
        print(f'    月令{month_zhi}({month_wx})克制日干{day_gan}({day_wx}) → 日干受克★')
    
    return year_gz, month_gz, day_gz, hour_gz, wx


def print_monthly_wuxing_calendar():
    """打印2026年月令五行旺衰日历，标注金气变化"""
    print(f'\n{"="*70}')
    print(f'  2026年月令五行旺衰推演（关注金气变化）')
    print(f'{"="*70}')
    
    months = [
        (1, '庚寅', '寅','木'), (2, '辛卯','卯','木'),
        (3, '壬辰','辰','土'), (4, '癸巳','巳','火'),
        (5, '甲午','午','火'), (6, '乙未','未','土'),
        (7, '丙申','申','金'), (8, '丁酉','酉','金'),
        (9, '戊戌','戌','土'), (10,'己亥','亥','水'),
        (11,'庚子','子','水'), (12,'辛丑','丑','土'),
    ]
    
    # 2026节气日期
    jieqi_dates = {
        '立春':'02-04','惊蛰':'03-06','清明':'04-05','立夏':'05-05',
        '芒种':'06-06','小暑':'07-07','立秋':'08-07','白露':'09-08',
        '寒露':'10-08','立冬':'11-07','大雪':'12-07','小寒':'01-05(2027)',
    }
    
    month_names = [
        (1,'正月(寅)'),(2,'二月(卯)'),(3,'三月(辰)'),(4,'四月(巳)'),
        (5,'五月(午)'),(6,'六月(未)'),(7,'七月(申)'),(8,'八月(酉)'),
        (9,'九月(戌)'),(10,'十月(亥)'),(11,'十一月(子)'),(12,'十二月(丑)'),
    ]
    
    print(f'\n┌──────┬──────────┬──────────┬──────┬──────────────────────────┐')
    print(f'│ 月序  │ 农历月   │ 月干支    │ 月支五行│ 金气状态                  │')
    print(f'├──────┼──────────┼──────────┼──────┼──────────────────────────┤')
    
    for seq, (nx, mn), (mx, mgz, mz, mwx) in zip(range(1,13), month_names, months):
        strength = get_month_wuxing_strength(mz)
        jin_state = strength['金']
        
        if jin_state == '旺':
            desc = '★★★★★ 金最旺，镍价止跌回升关键期'
        elif jin_state == '相':
            desc = '★★★★ 金气次旺，镍价有望企稳反弹'
        elif jin_state == '休':
            desc = '★★ 金气初生，关注底部构筑'
        elif jin_state == '囚':
            desc = '★ 金气衰弱，镍价承压'
        elif jin_state == '死':
            desc = '☆ 金气极弱，镍价受打压最甚'
        else:
            desc = ''
        
        marker = ' ← 高点' if mx == 5 else (' ← 当前' if seq == 6 else '')
        print(f'│ {seq:4d}月 │ {mn:8s} │ {mgz:8s} │ {mwx:4s} │ {desc:26s} │{marker}')
    
    print(f'└──────┴──────────┴──────────┴──────┴──────────────────────────┘')
    
    print(f'\n  ◆ 沪镍(属金)底部时间窗口推断：')
    print(f'    5月(巳火月)→6月(午火月)：火旺克金 ★ 镍价继续承压下跌')
    print(f'    7月(未土月)：未为燥土，火之余气仍在，但土能生金 ☆ 可能开始筑底')
    print(f'    8月(申金月)：申为庚金禄位，金临官 ★★★★★ 最有可能是底部区间')
    print(f'    9月(酉金月)：酉为辛金禄位，金帝旺 ★★★★★ 次优底部时间窗')
    print(f'    10月(戌土月)：戌为火库+燥土，土生金 ★★★ 确认回升')


def main():
    print('╔══════════════════════════════════════════════════════════════╗')
    print('║     沪镍合约底部时间推算 —— 四柱八字 + 奇门遁甲分析           ║')
    print('║     分析基准日：2026年5月6日（阶段高点）                       ║')
    print('╚══════════════════════════════════════════════════════════════╝')
    
    # ── 第一部分：四柱八字分析 ──
    print(f'\n{"#"*70}')
    print(f'#  第一部分：四柱八字深度分析')
    print(f'{"#"*70}')
    
    # 1.1 高点日分析
    high_dt = datetime(2026, 5, 6, 9, 30)
    yg, mg, dg, hg, wx_high = print_bazi_analysis('[高点] 阶段高点日', high_dt)
    
    print(f'\n  ◆ 高点日关键特征：')
    print(f'    日干{dg[0]}(金)坐{dg[1]}(土) → 庚金自坐戌土，有根')
    print(f'    但年柱丙午(火火)→月柱癸巳(水火)→火势猛烈')
    print(f'    火克金，年支午火=庚金沐浴败地 ★')
    print(f'    年干丙火=七杀克身，为阶段性顶部之象')
    print(f'    庚金虽得戌土生扶，但火势过旺而不得舒展')
    
    # 1.2 当前日分析
    now_dt = datetime(2026, 6, 28, 9, 30)
    yg2, mg2, dg2, hg2, wx_now = print_bazi_analysis('[当前] 当前日期', now_dt)
    
    print(f'\n  ◆ 当前日特征：')
    print(f'    日干{dg2[0]}(水)坐{dg2[1]}(水) → 癸水日元')
    print(f'    年柱丙午(火火)→月柱甲午(木火)→火力更强！')
    print(f'    甲木生丙火，木火通明，火势比5月更旺')
    print(f'    癸水被烈火炙烤，燥热至极 → 物极必反之兆')
    
    # ── 第二部分：五行月令推演 ──
    print(f'\n{"#"*70}')
    print(f'#  第二部分：2026年月令五行旺衰推演')
    print(f'{"#"*70}')
    print_monthly_wuxing_calendar()
    
    # ── 第三部分：奇门遁甲逐日扫描 ──
    print(f'\n{"#"*70}')
    print(f'#  第三部分：奇门遁甲关键日期排盘分析')
    print(f'{"#"*70}')
    
    # 关键分析日期（从6月底到10月，选取重要节点）
    key_dates = [
        # 当前期（确认下跌趋势）
        datetime(2026, 6, 30, 9, 30),
        
        # 未月关键日（7月7日小暑后，未土月）
        datetime(2026, 7, 7,  9, 30),
        datetime(2026, 7, 15, 9, 30),
        datetime(2026, 7, 22, 9, 30),
        datetime(2026, 7, 30, 9, 30),
        
        # 申月关键日（8月7日立秋后，申金月）- 核心窗口！
        datetime(2026, 8, 7,  9, 30),
        datetime(2026, 8, 10, 9, 30),
        datetime(2026, 8, 15, 9, 30),
        datetime(2026, 8, 20, 9, 30),
        datetime(2026, 8, 25, 9, 30),
        datetime(2026, 8, 30, 9, 30),
        
        # 酉月关键日（9月8日白露后，酉金月）
        datetime(2026, 9, 8,  9, 30),
        datetime(2026, 9, 15, 9, 30),
        datetime(2026, 9, 22, 9, 30),
        datetime(2026, 9, 30, 9, 30),
        
        # 戌月（10月8日寒露后）
        datetime(2026, 10, 8, 9, 30),
        datetime(2026, 10, 15, 9, 30),
    ]
    
    print(f'\n  正在对 {len(key_dates)} 个关键日期进行奇门排盘分析...\n')
    
    results = []
    for dt in key_dates:
        r = analyze_qimen_for_date(dt)
        results.append(r)
    
    # 打印奇门分析表格
    print(f'┌────────────┬──────────┬──────────┬────────┬──────┬──────────────┬──────────┐')
    print(f'│ 日期        │ 月干支    │ 日干支    │ 遁/局   │ 值符  │ 趋势判断      │ 评分     │')
    print(f'├────────────┼──────────┼──────────┼────────┼──────┼──────────────┼──────────┤')
    
    for r in results:
        if 'error' in r:
            print(f'│ {r["dt"].strftime("%m-%d")}      │ ERROR: {r["error"][:20]} │')
        else:
            bu_count = len(r['bullish'])
            be_count = len(r['bearish'])
            score = r['trend_score']
            trend = r['trend']
            
            # 高亮底部信号
            bottom_signal = ''
            if score >= 2:
                bottom_signal = ' ★★★'
            elif score >= 1:
                bottom_signal = ' ★'
            
            print(f'│ {r["dt"].strftime("%m-%d %a")} │ {r["month_gz"]:8s} │ {r["day_gz"]:8s} │ '
                  f'{r["dun"]}{r["bureau"]}({r["yuan"]}) │ {r["zf_star"]:4s} │ '
                  f'{trend:12s} │ {score:+3d}{bottom_signal:4s} │')
    
    print(f'└────────────┴──────────┴──────────┴────────┴──────┴──────────────┴──────────┘')
    
    # 打印详细分析
    print(f'\n{"─"*70}')
    print(f'  各日期详细信号分析')
    print(f'{"─"*70}')
    
    for r in results:
        if 'error' in r:
            continue
        
        score = r['trend_score']
        dt = r['dt']
        
        # 只有信号较强或较弱的日期才详细显示
        if abs(score) >= 1:
            indicator = '[BULL]' if score >= 2 else ('[NEUT]' if score >= 1 else '[BEAR]')
            print(f'\n  {indicator} {dt.strftime("%Y-%m-%d %a")} | '
                  f'{r["month_gz"]}月 {r["day_gz"]}日 | '
                  f'{r["dun"]}遁{r["bureau"]}局({r["yuan"]}) '
                  f'值符:{r["zf_star"]}→{r["zf_pos"]}宫')
            print(f'    旬空: {r["kong"]} | 马星: {r["ma_zhi"]}({r["ma_palace"]}宫)')
            print(f'    生门: {r["sheng_pos"]}宫 | 开门: {r["kai_pos"]}宫 | 戊(资金): {r["wu_pos"]}宫')
            
            if r['bullish']:
                for s in r['bullish']:
                    print(f'    + {s}')
            if r['bearish']:
                for s in r['bearish']:
                    print(f'    - {s}')
            print(f'    趋势: {r["trend"]}')
    
    # ── 第四部分：综合判断 ──
    print(f'\n{"#"*70}')
    print(f'#  第四部分：综合底部时间窗口推断')
    print(f'{"#"*70}')
    
    print(f'''
  +---------------------------------------------------------------+
  |              沪镍(金)底部时间窗口综合推断                      |
  +---------------------------------------------------------------+
  |                                                               |
  |  [分析逻辑]                                                    |
  |  1. 沪镍属金，火克金 -> 火旺则镍价受压                         |
  |  2. 土生金 -> 土旺月金气渐复                                   |
  |  3. 金月（申/酉）-> 金气临官/帝旺，镍价回升                    |
  |                                                               |
  |  [底部时间窗口（按概率排序）]                                   |
  |                                                               |
  |  [1] 第一窗口（最可能）：8月7日-9月7日【丙申月】                |
  |     - 申为庚金禄位，金临官                                    |
  |     - 丙火盖头申金，火金交战 -> 先跌后涨                       |
  |     - 底部可能在8月中旬（申金得令后）                           |
  |                                                               |
  |  [2] 第二窗口（次可能）：9月8日-10月7日【丁酉月】               |
  |     - 酉为辛金禄位，纯金之月                                    |
  |     - 如申月未完成筑底，酉月必见底                              |
  |                                                               |
  |  [3] 第三窗口（过渡期）：7月7日-8月6日【乙未月】                |
  |     - 未为燥土，火之余气+土生金                                 |
  |     - 可能是下跌减速/筑底的过渡期                               |
  |     - 但如果火气过旺，未月可能继续探底                          |
  |                                                               |
  |  [!] 重要提醒：                                                 |
  |  - 2026年丙午年，全年火势旺盛，金气受克                          |
  |  - 年干丙火=七杀，对镍(金)形成全年压制                          |
  |  - 即使申酉月金旺，年初的火势仍有余威                            |
  |  - 真正的趋势性回升可能在戌月(10月)以后                          |
  |                                                               |
  |  [关键日期节点]                                                 |
  |  - 7月7日(小暑)：进入未月，关注是否止跌                         |
  |  - 8月7日(立秋)：进入申月，核心观察期开始                        |
  |  - 8月15-25日：申月金气最盛时段，重点关注                        |
  |  - 9月8日(白露)：进入酉月，如果未見底则最后机会                  |
  |  - 10月8日(寒露)：进入戌月，确认底部是否已过                     |
  |                                                               |
  +---------------------------------------------------------------+
''')
    
    print(f'  [!] 免责声明：本分析基于传统术数方法论，仅供参考，不构成投资建议。')
    print(f'     期货交易风险极大，请结合基本面和技术面综合判断。')
    print(f'')

if __name__ == '__main__':
    main()
