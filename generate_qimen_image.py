# -*- coding: utf-8 -*-
"""
奇门遁甲排盘图片生成器
风格参考 qm.png: 仿古棕色背景，九宫格，每宫从上到下：
  八神 / 天盘星名+天盘干(红色大字) / 门名+地盘干 / 底部分割+状态

使用经过多案例验证的 qimen_engine_v2.py 引擎
"""

import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# 导入排盘引擎
sys.path.insert(0, os.path.dirname(__file__))
from qimen_engine_v2 import solve, get_xun_shou_gan, get_xun_kong, get_ma_xing

# ── 干支纪时 ─────────────────────────────────────────────────
TIANGAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DIZHI   = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

# ── 时辰划分（标准：子时23-1，每2小时一个时辰）─────────────────
# 亥时 21:00-23:00，戌时 19:00-21:00，以此类推
def get_hour_zhi(hour):
    """根据小时数返回时辰地支（标准划分）"""
    # 子时跨日: 23:00-次日1:00
    if hour == 23 or hour == 0:
        return '子'
    # 其余时辰每2小时: 丑1-3, 寅3-5, 卯5-7, 辰7-9, 巳9-11
    # 午11-13, 未13-15, 申15-17, 酉17-19, 戌19-21, 亥21-23
    hour_map = [
        (1,  3,  '丑'), (3,  5,  '寅'), (5,  7,  '卯'),
        (7,  9,  '辰'), (9,  11, '巳'), (11, 13, '午'),
        (13, 15, '未'), (15, 17, '申'), (17, 19, '酉'),
        (19, 21, '戌'), (21, 23, '亥'),
    ]
    for s, e, zhi in hour_map:
        if s <= hour < e:
            return zhi
    return '子'

def get_year_gan_zhi(year):
    """年干支：以公历年推算（立春前仍属上一年，此处简化按年份）"""
    gan_i = (year - 4) % 10
    zhi_i = (year - 4) % 12
    return TIANGAN[gan_i] + DIZHI[zhi_i]

# 2026年各节对应月干支（五虎遁年起月法，以节分月）
# 丙/辛年起庚寅，节气分界：
#   立春→庚寅, 惊蛰→辛卯, 清明→壬辰, 立夏→癸巳, 芒种→甲午, 小暑→乙未
#   立秋→丙申, 白露→丁酉, 寒露→戊戌, 立冬→己亥, 大雪→庚子, 小寒→辛丑
# 2026年各节气日期（精确值，用于月干支切换）：
# 立春: 2026-02-04, 惊蛰: 2026-03-06, 清明: 2026-04-05, 立夏: 2026-05-05
# 芒种: 2026-06-06, 小暑: 2026-07-07, 立秋: 2026-08-07, 白露: 2026-09-08
# 寒露: 2026-10-08, 立冬: 2026-11-07, 大雪: 2026-12-07, 小寒: 2027-01-05
MONTH_GZ_2026_BY_JIEQI = [
    # (月序, 月干支, 该月节气开始日(month, day))
    # 按节分月: 到达该节当天起换月
    ((2,  4),  '庚寅'),  # 立春
    ((3,  6),  '辛卯'),  # 惊蛰
    ((4,  5),  '壬辰'),  # 清明
    ((5,  5),  '癸巳'),  # 立夏
    ((6,  6),  '甲午'),  # 芒种 ← 6月6日在此
    ((7,  7),  '乙未'),  # 小暑
    ((8,  7),  '丙申'),  # 立秋
    ((9,  8),  '丁酉'),  # 白露
    ((10, 8),  '戊戌'),  # 寒露
    ((11, 7),  '己亥'),  # 立冬
    ((12, 7),  '庚子'),  # 大雪
]

def get_month_gan_zhi(year, month, day):
    """
    月干支：以节分月（五虎遁年起月法）
    2026年丙午年：正月起庚寅
    关键：芒种(6月6日)是五月的节，6月6日起为甲午月
    """
    if year != 2026:
        # 通用算法（简化版，仅考虑年干）
        year_gz = get_year_gan_zhi(year)
        year_gan = year_gz[0]
        YEAR_TO_MONTH1_GAN = {
            '甲': 2, '己': 2, '乙': 4, '庚': 4,
            '丙': 6, '辛': 6, '丁': 8, '壬': 8, '戊': 0, '癸': 0,
        }
        start = YEAR_TO_MONTH1_GAN[year_gan]
        # 简化：以公历月近似（不精确）
        month_seq = month - 1  # 粗略
        g = (start + month_seq) % 10
        z = (2 + month_seq) % 12
        return TIANGAN[g] + DIZHI[z]

    # 2026年精确版（以节分月）
    # 找当前日期属于哪个节月
    current = (month, day)
    result_gz = '庚寅'  # 默认正月（立春前）
    for (jm, jd), gz in MONTH_GZ_2026_BY_JIEQI:
        if current >= (jm, jd):
            result_gz = gz
    return result_gz

def get_day_gan_zhi(year, month, day):
    """
    日干支：以2019-07-29=丁卯日为已验证基准推算
    基准说明：qm.png明确标注2019年7月29日为丁卯日
    """
    from datetime import date
    BASE_DATE = date(2019, 7, 29)  # 丁卯日（已验证）
    BASE_POS  = 3                  # 丁卯在六十甲子中的序号（丁=3,卯=3,且3%10=3,3%12=3）
    d = date(year, month, day)
    delta = (d - BASE_DATE).days
    pos   = (BASE_POS + delta) % 60
    gan_i = pos % 10
    zhi_i = pos % 12
    return TIANGAN[gan_i] + DIZHI[zhi_i]

def get_hour_gan_zhi(day_gan, hour):
    """时干支：五鼠遁日起时法"""
    hour_zhi = get_hour_zhi(hour)
    zhi_i = DIZHI.index(hour_zhi)
    # 丙辛日子时起戊子
    DAY_GAN_TO_HOUR_GAN_START = {
        '甲': 0, '己': 0,   # 甲子
        '乙': 2, '庚': 2,   # 丙子
        '丙': 4, '辛': 4,   # 戊子
        '丁': 6, '壬': 6,   # 庚子
        '戊': 8, '癸': 8,   # 壬子
    }
    start_gan_i = DAY_GAN_TO_HOUR_GAN_START.get(day_gan, 0)
    hour_gan_i  = (start_gan_i + zhi_i) % 10
    return TIANGAN[hour_gan_i] + hour_zhi

def get_all_gz(dt):
    """四柱计算。注意：传统历法中，子时(23:00起)属于次日。"""
    from datetime import timedelta
    # 子时(23点)起算作次日
    if dt.hour >= 23:
        dt_adj = dt + timedelta(days=1)
    else:
        dt_adj = dt
    year_gz  = get_year_gan_zhi(dt_adj.year)
    month_gz = get_month_gan_zhi(dt_adj.year, dt_adj.month, dt_adj.day)
    day_gz   = get_day_gan_zhi(dt_adj.year, dt_adj.month, dt_adj.day)
    day_gan  = day_gz[0]
    hour_gz  = get_hour_gan_zhi(day_gan, dt.hour)
    return year_gz, month_gz, day_gz, hour_gz

def get_bureau_info(dt):
    """
    返回 (节气名, 阴阳遁, 局数, 元序)
    时家奇门超接法：每节含上中下三元，每元5天
    阳遁局数对照（超接/拆补法，依据docs/定局规则.md口诀）：
      冬至:1,7,4  小寒:2,8,5  大寒:3,9,6
      立春:8,5,2  雨水:9,6,3  惊蛰:1,7,4
      春分:3,9,6  清明:4,1,7  谷雨:5,2,8
      立夏:4,1,7  小满:5,2,8  芒种:6,3,9  ← 芒种上元=6局
    阴遁局数对照（超接/拆补法，依据docs/定局规则.md口诀）：
      夏至:9,3,6  小暑:8,2,5  大暑:7,1,4
      立秋:2,5,8  处暑:1,4,7  白露:9,3,6
      秋分:7,1,4  寒露:6,9,3  霜降:5,8,2
      立冬:6,9,3  小雪:5,8,2  大雪:4,7,1

    2026年精确节气时间：
      芒种: 6月6日 15:37  小暑: 7月7日  夏至: 6月21日
    上中下元分界：每元约5天（精确以实际历法为准）
    """
    # 子时(23点)起算作次日
    from datetime import date, timedelta as td_jq
    dt_adj_for_day = dt + td_jq(days=1) if dt.hour >= 23 else dt
    m, d, h = dt_adj_for_day.month, dt_adj_for_day.day, dt.hour
    curr = date(dt_adj_for_day.year, m, d)

    # 2026年节气日期（精确）
    # 局数依据：docs/定局规则.md（超接/拆补法口诀）
    # 阳遁歌：冬至惊蛰一七四，小寒二八五同推。春分大寒三九六，立春八五二相随。
    #         谷雨小满五二八，雨水九六三为期。清明立夏四一七，芒种六三九为宜。
    # 阴遁歌：夏至白露九三六，小暑八二五之间。大暑秋分七一四，立秋二五八循环。
    #         霜降小雪五八二，大雪四七一相关。处暑排来一四七，立冬寒露六九三。
    JIEQI_2026 = [
        # (月, 日, 节气名, 阴阳遁, [上元局,中元局,下元局])
        ( 1, 5,  '小寒', '阳', [2, 8, 5]),  # 小寒二八五
        ( 1,20,  '大寒', '阳', [3, 9, 6]),  # 春分大寒三九六
        ( 2, 4,  '立春', '阳', [8, 5, 2]),  # 立春八五二
        ( 2,19,  '雨水', '阳', [9, 6, 3]),  # 雨水九六三
        ( 3, 6,  '惊蛰', '阳', [1, 7, 4]),  # 冬至惊蛰一七四
        ( 3,20,  '春分', '阳', [3, 9, 6]),  # 春分大寒三九六
        ( 4, 5,  '清明', '阳', [4, 1, 7]),  # 清明立夏四一七
        ( 4,20,  '谷雨', '阳', [5, 2, 8]),  # 谷雨小满五二八
        ( 5, 5,  '立夏', '阳', [4, 1, 7]),  # 清明立夏四一七
        ( 5,21,  '小满', '阳', [5, 2, 8]),  # 谷雨小满五二八
        ( 6, 6,  '芒种', '阳', [6, 3, 9]),  # 芒种六三九为宜
        ( 6,21,  '夏至', '阴', [9, 3, 6]),  # 夏至白露九三六
        ( 7, 7,  '小暑', '阴', [8, 2, 5]),  # 小暑八二五
        ( 7,22,  '大暑', '阴', [7, 1, 4]),  # 大暑秋分七一四
        ( 8, 7,  '立秋', '阴', [2, 5, 8]),  # 立秋二五八
        ( 8,23,  '处暑', '阴', [1, 4, 7]),  # 处暑排来一四七
        ( 9, 8,  '白露', '阴', [9, 3, 6]),  # 夏至白露九三六
        ( 9,23,  '秋分', '阴', [7, 1, 4]),  # 大暑秋分七一四
        (10, 8,  '寒露', '阴', [6, 9, 3]),  # 立冬寒露六九三
        (10,23,  '霜降', '阴', [5, 8, 2]),  # 霜降小雪五八二
        (11, 7,  '立冬', '阴', [6, 9, 3]),  # 立冬寒露六九三
        (11,22,  '小雪', '阴', [5, 8, 2]),  # 霜降小雪五八二
        (12, 7,  '大雪', '阴', [4, 7, 1]),  # 大雪四七一
        (12,22,  '冬至', '阳', [1, 7, 4]),  # 冬至惊蛰一七四
    ]

    # 找当前所在节气段
    cur_jieqi = None
    cur_dun = '阳'
    cur_bureaus = [6,3,9]
    for jm, jd, jname, jdun, jb in JIEQI_2026:
        jdate = date(2026, jm, jd)
        if curr >= jdate:
            cur_jieqi = jname
            cur_dun   = jdun
            cur_bureaus = jb
            jieqi_start = jdate

    if cur_jieqi is None:
        return '小寒', '阳', 7, '上元'

    # ── 拆补法定元：按日干支的"符头"（最近甲/己日）确定 ──
    # 符头地支 子午卯酉→上元, 寅申巳亥→中元, 辰戌丑未→下元
    SHANG = {'子','午','卯','酉'}
    ZHONG = {'寅','申','巳','亥'}
    XIA   = {'辰','戌','丑','未'}

    # 向前查找最近的甲日或己日（符头）
    from datetime import timedelta
    check = curr
    fu_tou_gz = None
    for _ in range(10):  # 最多回退10天必能找到
        dgz = get_day_gan_zhi(check.year, check.month, check.day)
        dg, dz = dgz[0], dgz[1]
        if dg in ('甲', '己'):
            fu_tou_gz = dgz
            break
        check = check - timedelta(days=1)

    if fu_tou_gz is None:
        # 极端情况fallback
        days_since = (curr - jieqi_start).days
        if days_since < 5:
            yuan = '上元'
            bureau = cur_bureaus[0]
        elif days_since < 10:
            yuan = '中元'
            bureau = cur_bureaus[1]
        else:
            yuan = '下元'
            bureau = cur_bureaus[2]
    else:
        fz = fu_tou_gz[1]
        if fz in SHANG:
            yuan = '上元'
            bureau = cur_bureaus[0]
        elif fz in ZHONG:
            yuan = '中元'
            bureau = cur_bureaus[1]
        else:
            yuan = '下元'
            bureau = cur_bureaus[2]

    return cur_jieqi, cur_dun, bureau, yuan


# ── 九宫格行列位置 ─────────────────────────────────────────────
# 洛书宫位布局:
#  4  9  2
#  3  5  7
#  8  1  6
PALACE_TO_RC = {
    4: (0, 0), 9: (0, 1), 2: (0, 2),
    3: (1, 0), 5: (1, 1), 7: (1, 2),
    8: (2, 0), 1: (2, 1), 6: (2, 2),
}

# 宫位与卦名
PALACE_NAME = {
    1:'坎', 2:'坤', 3:'震', 4:'巽',
    5:'中', 6:'乾', 7:'兑', 8:'艮', 9:'离'
}


def draw_qimen_chart(result, output_path, dt_str='', jieqi='', dun='', bureau_num=0, yuan='上元'):
    """绘制奇门遁甲盘面，仿 qm.png 风格"""

    # ── 颜色 ──────────────────────────────────────────────────
    BG_COLOR    = (205, 175, 122)   # 仿古棕黄背景
    GRID_COLOR  = (110, 65, 15)     # 深棕格线
    RED_COLOR   = (195, 25, 25)     # 红色（天盘干）
    DARK_RED    = (140, 40, 0)      # 暗红（天盘星名）
    BLACK_COLOR = (15, 15, 15)      # 黑色文字
    BLUE_COLOR  = (25, 75, 175)     # 蓝色（重要信息）
    GREEN_COLOR = (0, 120, 60)      # 绿色（马星）
    GRAY_COLOR  = (120, 120, 120)   # 灰色（空亡）
    CELL_BG     = (228, 200, 155)   # 宫格内背景
    CENTER_BG   = (195, 160, 100)   # 中宫背景

    # ── 尺寸 ──────────────────────────────────────────────────
    IMG_W    = 880
    IMG_H    = 1080
    HEADER_H = 195
    GRID_X   = 55
    GRID_Y   = HEADER_H + 15
    CELL_W   = (IMG_W - GRID_X * 2) // 3    # ≈257
    CELL_H   = 225
    GRID_W   = CELL_W * 3
    GRID_H   = CELL_H * 3
    LW       = 3   # 格线宽

    img  = Image.new('RGB', (IMG_W, IMG_H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # ── 字体 ──────────────────────────────────────────────────
    def load_font(size):
        for fp in [
            'C:/Windows/Fonts/simhei.ttf',
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/simsun.ttc',
        ]:
            if os.path.exists(fp):
                try:
                    return ImageFont.truetype(fp, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    f_tiny  = load_font(17)
    f_sm    = load_font(25)
    f_mid   = load_font(28)
    f_lg    = load_font(48)
    f_hdr   = load_font(23)
    f_title = load_font(34)

    # ── 排盘数据 ───────────────────────────────────────────────
    ci = result['chart_info']
    dp = result['di_pan']
    hv = result['hv_stems']
    hs = result['hv_stars']
    pd_doors = result['palace_doors']
    pg = result['palace_gods']       # 天盘八神
    eg = result['earth_gods']        # 地盘八神（旬首宫起）
    kong_palaces = ci.get('kong_palaces', [])
    kong_pair    = ci.get('kong_pair', ('',''))
    ma_palace    = ci.get('ma_palace', 0)
    ma_zhi       = ci.get('ma_zhi', '')
    # 天盘值符落宫：值符随时干，中宫寄2宫
    _zf_heaven = ci.get('zhi_fu_heaven_pos', ci.get('zhi_fu_pos', 0))
    zhi_fu_pos   = 2 if _zf_heaven == 5 else _zf_heaven  # 寄宫处理
    zhi_shi_pos  = ci.get('zhi_shi_pos', 0)
    # 寄宫数据
    jigan_stems    = result.get('jigan_stems', {})     # 天盘寄干（天芮落宫的寄干）
    hv_stars_jigan = result.get('hv_stars_jigan', {})  # 寄星（天禽跟随天芮）
    earth_jigan    = result.get('earth_jigan', {})      # 地盘寄干（坤2宫寄中5宫地盘干）

    # ── 头部信息 ───────────────────────────────────────────────
    cx_center = IMG_W // 2
    draw.text((cx_center, 14), '奇门遁甲时家排盘',
              font=f_title, fill=DARK_RED, anchor='mt')

    lh = 28
    y0 = 55
    draw.text((GRID_X, y0),      f'时间：{dt_str}',           font=f_hdr, fill=BLACK_COLOR)
    # 旬首完整名称：甲子戊/甲戌己/甲申庚/甲午辛/甲辰壬/甲寅癸
    XUN_FULL = {'戊':'甲子戊','己':'甲戌己','庚':'甲申庚','辛':'甲午辛','壬':'甲辰壬','癸':'甲寅癸'}
    xun_shou_full = XUN_FULL.get(ci['xun_shou_gan'], ci['xun_shou_gan'])
    draw.text((GRID_X, y0+lh),   f'节气：{jieqi}{yuan}  {dun}遁{bureau_num}局  旬首：{xun_shou_full}',
              font=f_hdr, fill=BLACK_COLOR)
    draw.text((GRID_X, y0+lh*2), f'四柱：{ci["time"]}',       font=f_hdr, fill=BLACK_COLOR)
    draw.text((GRID_X, y0+lh*3),
              f'值符：{ci["zhi_fu_star"]}落{zhi_fu_pos}宫    '
              f'值使：{ci["zhi_shi_door"]}落{zhi_shi_pos}宫',
              font=f_hdr, fill=BLUE_COLOR)
    kong_str = f'{kong_pair[0]}{kong_pair[1]}' if kong_pair else ''
    draw.text((GRID_X, y0+lh*4),
              f'旬空：{kong_str}（{"/".join(str(p)+"宫" for p in kong_palaces)}）    '
              f'驿马：{ma_zhi}（{ma_palace}宫）',
              font=f_hdr, fill=BLACK_COLOR)

    # ── 九宫格外框 ─────────────────────────────────────────────
    draw.rectangle(
        [GRID_X-LW, GRID_Y-LW, GRID_X+GRID_W+LW, GRID_Y+GRID_H+LW],
        outline=GRID_COLOR, width=LW*2
    )
    for i in range(1, 3):
        x = GRID_X + CELL_W * i
        draw.line([(x, GRID_Y), (x, GRID_Y+GRID_H)], fill=GRID_COLOR, width=LW)
        y = GRID_Y + CELL_H * i
        draw.line([(GRID_X, y), (GRID_X+GRID_W, y)], fill=GRID_COLOR, width=LW)

    # ── 绘制各宫 ───────────────────────────────────────────────
    def text_w(text, font):
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0]

    def text_h(text, font):
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[3] - bb[1]

    for palace in range(1, 10):
        row, col = PALACE_TO_RC[palace]
        cx = GRID_X + col * CELL_W
        cy = GRID_Y + row * CELL_H
        cw, ch = CELL_W, CELL_H
        px = cx + LW + 1
        py = cy + LW + 1
        pw = cw - LW * 2 - 2
        ph = ch - LW * 2 - 2

        # 宫格背景
        bg = CENTER_BG if palace == 5 else CELL_BG
        draw.rectangle([px, py, px+pw, py+ph], fill=bg)

        # ── 中宫：只显示地盘干 ────────────────────────────────
        if palace == 5:
            stem5 = dp.get(5, '')
            tw = text_w(stem5, f_lg)
            th = text_h(stem5, f_lg)
            draw.text((cx + cw//2 - tw//2, cy + ch//2 - th//2),
                      stem5, font=f_lg, fill=BLACK_COLOR)
            # 宫号
            draw.text((cx + cw - 24, cy + ch - 22),
                      '5', font=f_tiny, fill=GRID_COLOR)
            continue

        # 获取数据
        god_name  = pg.get(palace, '')
        star_name = hs.get(palace, '')
        hv_stem   = hv.get(palace, '')
        door_name = pd_doors.get(palace, '')
        dp_stem   = dp.get(palace, '')

        PAD   = 10   # 左边距
        y_cur = py + 8

        # ── 右上角：空亡 ○（蓝色圆圈，偏左）& 马星（绿色，偏右）──
        R = 9  # 圆圈半径
        kong_right = px + pw - 36  # 空亡圆圈中心x（偏左）
        ma_right   = px + pw - 18  # 马星文字x（偏右）
        has_kong = palace in kong_palaces
        has_ma   = palace == ma_palace

        if has_kong and has_ma:
            # 两者同时出现：空亡左，马星右
            draw.ellipse(
                [kong_right - R, py + 12, kong_right + R, py + 12 + R * 2],
                outline=BLUE_COLOR, width=2
            )
            draw.text((ma_right, py + 10), '马', font=f_tiny, fill=GREEN_COLOR)
        elif has_kong:
            # 仅空亡：居中偏左
            draw.ellipse(
                [kong_right - R, py + 12, kong_right + R, py + 12 + R * 2],
                outline=BLUE_COLOR, width=2
            )
        elif has_ma:
            # 仅马星：居中
            draw.text((ma_right + 6, py + 10), '马', font=f_tiny, fill=GREEN_COLOR)

        # ── 行1：天盘八神（左，字号加大） ───────────
        if god_name:
            draw.text((px + PAD, y_cur + 2), god_name, font=f_sm, fill=BLACK_COLOR)
        y_cur += 32

        # ── 行2：天盘星名（值符宫红色，其他黑色）& 寄星（蓝色）& 天盘干（值符宫红色，其他黑色）& 寄干（蓝色）──
        star_color = RED_COLOR if palace == zhi_fu_pos else BLACK_COLOR
        stem_color = RED_COLOR if palace == zhi_fu_pos else BLACK_COLOR
        if star_name:
            draw.text((px + PAD, y_cur), star_name, font=f_mid, fill=star_color)
            # 寄星：天禽跟随天芮，蓝色显示
            jigan_star = hv_stars_jigan.get(palace, '')
            if jigan_star:
                star_tw = text_w(star_name, f_mid)
                draw.text((px + PAD + star_tw + 6, y_cur),
                          jigan_star, font=f_mid, fill=BLUE_COLOR)
        if hv_stem:
            tw = text_w(hv_stem, f_lg)
            # 寄干（天盘）：天禽带的5宫地盘干，蓝色显示，在天盘干右边
            jigan_stem = jigan_stems.get(palace, '')
            if jigan_stem:
                ji_tw = text_w(jigan_stem, f_mid)
                # 天盘干左移，给寄干留空间
                hv_x = px + pw - tw - ji_tw - PAD - 4
                draw.text((hv_x, y_cur - 8),
                          hv_stem, font=f_lg, fill=stem_color)
                # 寄干在右边
                draw.text((px + pw - ji_tw - PAD, y_cur + 4),
                          jigan_stem, font=f_mid, fill=BLUE_COLOR)
            else:
                draw.text((px + pw - tw - PAD, y_cur - 8),
                          hv_stem, font=f_lg, fill=stem_color)
        y_cur += 46

        # ── 行3：门名（值使门红色，其他黑色）& 地盘干（右，大字黑色）& 寄干（蓝色）─────
        door_color = RED_COLOR if palace == zhi_shi_pos else BLACK_COLOR
        if door_name:
            draw.text((px + PAD, y_cur), door_name, font=f_mid, fill=door_color)
        if dp_stem:
            tw = text_w(dp_stem, f_lg)
            # 地盘寄干：坤2宫寄中5宫的地盘干，蓝色显示，在地盘干右边
            earth_ji = earth_jigan.get(palace, '')
            if earth_ji:
                ji_tw = text_w(earth_ji, f_mid)
                dp_x = px + pw - tw - ji_tw - PAD - 4
                draw.text((dp_x, y_cur - 8),
                          dp_stem, font=f_lg, fill=BLACK_COLOR)
                draw.text((px + pw - ji_tw - PAD, y_cur + 4),
                          earth_ji, font=f_mid, fill=BLUE_COLOR)
            else:
                draw.text((px + pw - tw - PAD, y_cur - 8),
                          dp_stem, font=f_lg, fill=BLACK_COLOR)
        y_cur += 46

        # ── 分割线 ──────────────────────────────────────────
        draw.line([(px + PAD, y_cur), (px + pw - PAD, y_cur)],
                  fill=GRID_COLOR, width=1)
        y_cur += 7

        # ── 行4：底部标记区 ──────────────────────────────────
        # 地盘八神（左）：从旬首宫起排
        earth_god = eg.get(palace, '')
        if earth_god:
            draw.text((px + PAD, y_cur), earth_god, font=f_sm, fill=BLACK_COLOR)

        # 特殊标记（右侧，小字叠加）
        marks = []
        if palace == zhi_fu_pos:
            marks.append(('值符★', BLUE_COLOR))
        if palace == zhi_shi_pos:
            marks.append(('值使◆', BLUE_COLOR))

        mk_y = y_cur
        for mk_txt, mk_color in marks:
            tw_mk = text_w(mk_txt, f_tiny)
            draw.text((px + pw - tw_mk - PAD, mk_y), mk_txt, font=f_tiny, fill=mk_color)
            mk_y += 18

        # 宫号（右下角）
        draw.text((px + pw - 22, py + ph - 22),
                  str(palace), font=f_tiny, fill=GRID_COLOR)

    # ── 底部说明 ───────────────────────────────────────────────
    footer_y = GRID_Y + GRID_H + 18
    draw.text((GRID_X, footer_y),
              f'本宫图藏  {ci["time"]}',
              font=f_sm, fill=DARK_RED)

    # ── 保存 ───────────────────────────────────────────────────
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'PNG', dpi=(150, 150))
    print(f'已保存: {output_path}')
    return output_path


def main():
    """生成当前时刻的奇门遁甲盘"""
    now = datetime.now()

    year_gz, month_gz, day_gz, hour_gz = get_all_gz(now)
    print(f'时间: {now.strftime("%Y年%m月%d日 %H:%M")}')
    print(f'四柱: {year_gz} {month_gz} {day_gz} {hour_gz}')

    jieqi_name, dun, bureau_num, yuan = get_bureau_info(now)
    print(f'节气: {jieqi_name}{yuan}, {dun}遁{bureau_num}局')

    result = solve(year_gz, month_gz, day_gz, hour_gz, jieqi_name, dun, bureau_num)
    ci = result['chart_info']

    print('--- 排盘结果 ---')
    print('地盘:', {k: v for k, v in sorted(result['di_pan'].items())})
    print('天盘:', {k: v for k, v in sorted(result['hv_stems'].items())})
    print('八门:', {k: v for k, v in sorted(result['palace_doors'].items()) if v})
    print('天盘八神:', {k: v for k, v in sorted(result['palace_gods'].items()) if k != 5})
    print('地盘八神:', {k: v for k, v in sorted(result['earth_gods'].items()) if k != 5})
    print('旬首:', ci['xun_shou_gan'])
    print('值符:', ci['zhi_fu_star'], '落', ci['zhi_fu_pos'], '宫')
    print('值使:', ci['zhi_shi_door'], '落', ci['zhi_shi_pos'], '宫')
    print('旬空:', ci['kong_pair'], '-> 宫位', ci['kong_palaces'])
    print('驿马:', ci['ma_zhi'], '-> ', ci['ma_palace'], '宫')

    dt_str = now.strftime('%Y年%m月%d日 %H:%M')
    ts = now.strftime('%Y%m%d_%H%M')
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'output', f'qimen_{ts}.png'
    )

    draw_qimen_chart(
        result, output_path,
        dt_str=dt_str,
        jieqi=jieqi_name,
        dun=dun,
        bureau_num=bureau_num,
        yuan=yuan
    )
    return output_path


if __name__ == '__main__':
    out = main()
    print(f'\n生成完毕: {out}')
