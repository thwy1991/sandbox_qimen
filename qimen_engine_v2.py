# -*- coding: utf-8 -*-
"""
奇门遁甲排盘引擎 V2（按排盘规则.md重写）

核心规则（依据 docs/排盘规则.md）：
总顺序：地盘 → 天盘 → 八门（人盘）→ 八神（神盘）

【地盘】
  从局数宫起，阳遁顺飞(+1)，阴遁逆飞(-1)，布戊己庚辛壬癸丁丙乙9干

【天盘】"值符随时干"
  1. 值符 = 旬首干所在地盘宫位 对应的固定宫星
  2. 将值符星转到时干所在地盘宫位
  3. 其余九星从该宫顺时针依次排列
  4. 各星带走其原始固定宫的地盘奇仪 → 天盘干

【八门（人盘）】"值使随时支"
  - 固定宫门：休1 死2 伤3 杜4 景9 开6 惊7 生8
  - 值使 = 旬首干所在地盘宫位 对应的固定门
  - 从旬首宫开始，阳遁顺数/阴遁逆数 到时支所在地盘宫位
  - 将值使门布到该宫位，其余八门从该宫顺时针依次排列

【八神（神盘）】"小值符随大值符"
  - 固定顺序：值符→腾蛇→太阴→六合→白虎→玄武→九地→九天
  - 小值符落在大值符（天盘值符星）所在宫位
  - 阳遁：从该宫顺时针排布
  - 阴遁：从该宫逆时针排布
"""

TIANGAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DIZHI   = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

# 宫位对应地支（洛书方位）
PALACE_DIZHI = {
    1: ['子'],          # 坎-子
    2: ['未','申'],     # 坤-未申
    3: ['卯'],          # 震-卯
    4: ['辰','巳'],     # 巽-辰巳
    5: [],              # 中宫-无地支
    6: ['戌','亥'],     # 乾-戌亥
    7: ['酉'],          # 兑-酉
    8: ['丑','寅'],     # 艮-丑寅
    9: ['午'],          # 离-午
}
DIZHI_TO_PALACE = {}
for _p, _zl in PALACE_DIZHI.items():
    for _z in _zl:
        DIZHI_TO_PALACE[_z] = _p

# 旬空对照表
XUN_KONG = {
    0:  ('戌','亥'),   # 甲子旬
    10: ('申','酉'),   # 甲戌旬
    20: ('午','未'),   # 甲申旬
    30: ('辰','巳'),   # 甲午旬
    40: ('寅','卯'),   # 甲辰旬
    50: ('子','丑'),   # 甲寅旬
}

# 驿马：以时支定马（口诀：申子辰马在寅 / 寅午戌马在申 / 巳酉丑马在亥 / 亥卯未马在巳）
MA_MAP = {
    '申':'寅','子':'寅','辰':'寅',
    '寅':'申','午':'申','戌':'申',
    '亥':'巳','卯':'巳','未':'巳',
    '巳':'亥','酉':'亥','丑':'亥',
}

# 九星固定宫位
STARS_BY_PALACE = {
    1:'天蓬', 2:'天芮', 3:'天冲', 4:'天辅', 5:'天禽',
    6:'天心', 7:'天柱', 8:'天任', 9:'天英'
}

# 八门固定宫位（中5宫无门）
DOORS_BY_PALACE = {
    1:'休门', 2:'死门', 3:'伤门', 4:'杜门',
    6:'开门', 7:'惊门', 8:'生门', 9:'景门'
}

# 八神固定顺序（阳遁顺时针、阴遁逆时针均用此序）
DEITIES_ORDER = ['值符','腾蛇','太阴','六合','白虎','玄武','九地','九天']

# 旬首干（甲所化）
XUNHEAD_GAN = {0:'戊', 10:'己', 20:'庚', 30:'辛', 40:'壬', 50:'癸'}

# 洛书顺时针宫位顺序（8宫，不含中5）- 用于天盘、八神
# 正确顺时针（按九宫格方位顺序）：
#   下中(1坎)→左下(8艮)→左中(3震)→左上(4巽)→上中(9离)→右上(2坤)→右中(7兑)→右下(6乾)
CLOCKWISE_8 = [1, 8, 3, 4, 9, 2, 7, 6]   # 顺时针8宫（天盘/八神用）
COUNTER_8   = [1, 6, 7, 2, 9, 4, 3, 8]   # 逆时针8宫（顺时针反转，从1起）

# 八门专用：按宫位数字序（1→2→3→4→5→6→7→8→9，含中5宫）
# 注意：中5宫有号无门，但数步时必须计入。布门时用CLOCKWISE_8跳过5宫。
# 文档举例验证：
#   阳遁：从7宫顺数到4宫 = 7→8→9→1→2→3→4（6步，含5则7步？）
#   含5路径验证：7(甲戌6)→8→9→1→2→3→4(庚辰6)→ 索引(6+6)%9=3, path[3]=4 ✓
#   癸亥验证：2(甲寅0)→3→4→5→6→7→8→9→1→2(癸亥9)→ 索引(1+9)%9=1, path[1]=2 ✓
DOOR_NUM_SEQ  = [1, 2, 3, 4, 5, 6, 7, 8, 9]   # 数字序顺时针（含中5）
DOOR_NUM_RSEQ = [1, 9, 8, 7, 6, 5, 4, 3, 2]   # 数字序逆时针（含中5）


def jiazi_pos(gan, zhi):
    """六十甲子中的序号 (0-59)"""
    gi = TIANGAN.index(gan)
    zi = DIZHI.index(zhi)
    for n in range(60):
        if n % 10 == gi and n % 12 == zi:
            return n
    return -1


def get_xun_shou_gan(hour_gan, hour_zhi):
    """根据时柱确定旬首干"""
    pos = jiazi_pos(hour_gan, hour_zhi)
    if pos < 0:
        return '戊'
    xun_start = (pos // 10) * 10
    return XUNHEAD_GAN.get(xun_start, '戊')


def get_di_pan(dun, bureau):
    """
    排地盘：从局数宫起，阳顺阴逆布戊己庚辛壬癸丁丙乙
    """
    seq = ['戊','己','庚','辛','壬','癸','丁','丙','乙']
    dp = {}
    for i, ch in enumerate(seq):
        if dun == '阳':
            pos = (bureau - 1 + i) % 9 + 1
        else:
            pos = (bureau - 1 - i) % 9 + 1
        dp[pos] = ch
    return dp


def rotate_from(start_palace, n_steps, clockwise=True):
    """
    从 start_palace 在顺/逆时针路径上走 n_steps 步，返回到达的宫位
    注意：中宫5不在路径中
    """
    path = CLOCKWISE_8 if clockwise else COUNTER_8
    if start_palace == 5:
        start_palace = 2  # 中宫寄坤2
    if start_palace not in path:
        start_palace = 1
    si = path.index(start_palace)
    return path[(si + n_steps) % 8]


def calc_heaven_plate(di_pan, dun, xun_shou_pos, hour_gan_pos):
    """
    计算天盘干 —— "值符随时干"

    值符（旧宫）→ 时干宫（新宫），其余九星按顺时针顺序跟随排列。
    各星带走其原始固定宫的地盘干 → 成为天盘干。

    寄宫规则（天禽寄坤2宫）：
      - 天禽星(5宫)永远寄于坤2宫，跟随天芮星一起转动
      - 天芮转动时带走2宫的地盘干（主干），天禽带走5宫的地盘干（寄干）
      - 中宫5的天盘干同坤2宫

    九星固定顺序（顺时针布列，不论阴阳遁永远顺时针）：
      天蓬→天任→天冲→天辅→天英→天芮→天柱→天心（8星，天禽不在此列）

    实现：
      1. 确定值符星 = 旬首宫的固定星
      2. 将值符转到时干宫
      3. 其余8宫顺时针依次填入（顺时针从时干宫走）
      4. 天芮落宫附带寄干（5宫地盘干），天禽跟随
    """
    # 值符星是旬首宫的固定星
    zhi_fu_star = STARS_BY_PALACE.get(xun_shou_pos, '天蓬')

    # 九星顺时针顺序（按规则：天蓬→天任→天冲→天辅→天英→天芮→天柱→天心）
    STAR_CLOCKWISE = ['天蓬','天任','天冲','天辅','天英','天芮','天柱','天心']

    # 确定值符星在顺序中的位置
    if zhi_fu_star in STAR_CLOCKWISE:
        zf_si = STAR_CLOCKWISE.index(zhi_fu_star)
    elif zhi_fu_star == '天禽':
        zf_si = STAR_CLOCKWISE.index('天芮')  # 天禽寄坤2宫，跟随天芮一起转
    else:
        zf_si = 0

    # 值符落在时干宫，从时干宫出发顺时针布8星
    start_palace = hour_gan_pos if hour_gan_pos != 5 else 2

    hv_stems = {}
    jigan_stems = {}  # 寄干：天禽跟随天芮，带5宫地盘干
    for step in range(8):
        # 第step个宫（顺时针从时干宫）
        target_palace = rotate_from(start_palace, step, clockwise=True)
        # 对应的星是第(zf_si + step) % 8个星
        star = STAR_CLOCKWISE[(zf_si + step) % 8]
        # 找该星在固定盘中的原始宫，取地盘干
        orig_palace = [k for k, v in STARS_BY_PALACE.items() if v == star]
        if orig_palace:
            hv_stems[target_palace] = di_pan.get(orig_palace[0], '')
        else:
            hv_stems[target_palace] = ''

        # 寄宫：天芮星转动时，天禽星（5宫）跟随，带5宫地盘干作为寄干
        if star == '天芮':
            jigan_stems[target_palace] = di_pan.get(5, '')

    # 中宫5：天禽寄坤2宫（天芮所在），取坤2宫的天盘干和寄干
    hv_stems[5] = hv_stems.get(2, '')
    if 2 in jigan_stems:
        jigan_stems[5] = jigan_stems[2]

    return hv_stems, jigan_stems


def calc_doors(di_pan, dun, xun_shou_pos, hour_gan, hour_zhi):
    """
    八门（人盘）—— "值使随时支"

    核心规则（依据 docs/八门的排盘方法.md）：
    1. 值使 = 旬首宫（地盘）的固定门
    2. 步数 = 时柱在六十甲子中的序号 - 旬首在六十甲子中的序号（旬内偏移，0~9）
    3. 从旬首宫起，按宫位数字序：
       - 阳遁顺数（1→2→3→4→6→7→8→9→1...）走steps步
       - 阴遁逆数（1→9→8→7→6→4→3→2→1...）走steps步
       落宫即为值使落宫
    4. 将值使门布到该宫，其余七门从该宫按数字序顺时针（1→2→3→4→6→7→8→9）依次填入

    文档验证：
      阳遁，甲戌旬(#10)→7宫，庚辰(#16)，步数=6，顺走：7→8→9→1→2→3→4 值使惊门落4宫 ✓
      阴遁，甲子旬(#0)→1宫，丁卯(#3)，步数=3，逆走：1→9→8→7 值使休门落7宫 ✓
    """
    # 旬首宫（路径中用原始宫位，5宫在路径中有位置）
    start_p = xun_shou_pos

    # 值使门 = 旬首宫的固定门（5宫无门，寄坤2宫取死门）
    door_origin = start_p if start_p != 5 else 2
    zhi_shi_door = DOORS_BY_PALACE.get(door_origin, '休门')

    # 计算旬内步数：时柱序号 - 旬首序号
    hour_jiazi = jiazi_pos(hour_gan, hour_zhi)
    # 旬首对应的甲子序号 = xun_start_offset * 10
    # xun_shou_gan -> XUNHEAD_GAN逆查
    XUNHEAD_GAN_INV = {v: k for k, v in XUNHEAD_GAN.items()}
    xun_gan = None
    for p, g in di_pan.items():
        if p == xun_shou_pos:
            # 旬首宫的地盘干是旬首奇仪，需用旬首甲干（不是奇仪）
            break
    # 用 jiazi_pos 确定旬首在甲子表中的位置
    # 旬首干 = xun_shou_gan（由 get_xun_shou_gan 得到），但这里我们只有 xun_shou_pos
    # 改为：直接通过 hour_jiazi // 10 * 10 得到旬起始
    xun_jiazi_start = (hour_jiazi // 10) * 10
    steps = hour_jiazi - xun_jiazi_start  # 0~9

    # 从旬首宫按路径走steps步
    if dun == '阳':
        path = DOOR_NUM_SEQ
    else:
        path = DOOR_NUM_RSEQ

    if start_p not in path:
        start_p = 1

    si_start = path.index(start_p)
    zhi_shi_palace_raw = path[(si_start + steps) % len(path)]

    # 值使落5宫时，寄到2宫（坤宫）
    zhi_shi_palace = zhi_shi_palace_raw if zhi_shi_palace_raw != 5 else 2

    # 八门固定顺序（顺时针）：休→生→伤→杜→景→死→惊→开
    DOOR_ORDER = ['休门','生门','伤门','杜门','景门','死门','惊门','开门']

    # 值使门在门序中的位置
    door_si = DOOR_ORDER.index(zhi_shi_door) if zhi_shi_door in DOOR_ORDER else 0

    # 从值使落宫起，按视觉顺时针（洛书方位）布八门
    # 文档举例验证：值使惊门落4宫→顺时针下一宫是9宫(离)，而非6宫(乾)
    # 故布门须用 CLOCKWISE_8 [1,8,3,4,9,2,7,6]，不能用数字序
    si_val = CLOCKWISE_8.index(zhi_shi_palace) if zhi_shi_palace in CLOCKWISE_8 else 0
    palace_doors = {}
    for step in range(8):
        target_palace = CLOCKWISE_8[(si_val + step) % 8]
        door = DOOR_ORDER[(door_si + step) % 8]
        palace_doors[target_palace] = door

    palace_doors[5] = palace_doors.get(2, '')  # 中宫寄坤2

    return palace_doors, zhi_shi_door, zhi_shi_palace


def _calc_gods_core(dun, start_p):
    """八神排布核心：从 start_p 起，阳顺阴逆排布 DEITIES_ORDER"""
    start_p = start_p if start_p != 5 else 2

    if start_p not in CLOCKWISE_8:
        start_p = 2

    gods = {}
    if dun == '阳':
        for step in range(8):
            target_palace = rotate_from(start_p, step, clockwise=True)
            gods[target_palace] = DEITIES_ORDER[step]
    else:
        for step in range(8):
            target_palace = rotate_from(start_p, step, clockwise=False)
            gods[target_palace] = DEITIES_ORDER[step]

    gods[5] = gods.get(2, DEITIES_ORDER[0])  # 中宫寄坤2
    return gods


def calc_gods(dun, heaven_zf_palace):
    """
    天盘八神 —— 小值符随大值符（天盘值符落宫 = 时干宫）
    阳遁顺时针，阴遁逆时针
    """
    return _calc_gods_core(dun, heaven_zf_palace)


def calc_earth_gods(dun, xun_shou_pos):
    """
    地盘八神 —— 小值符随地盘值符（旬首宫）
    阳遁顺时针，阴遁逆时针
    """
    return _calc_gods_core(dun, xun_shou_pos)


def get_xun_kong(hour_gan, hour_zhi):
    """计算旬空（空亡）地支对及对应宫位"""
    pos = jiazi_pos(hour_gan, hour_zhi)
    if pos < 0:
        return ('戌','亥'), []
    xun_start = (pos // 10) * 10
    kong_pair = XUN_KONG.get(xun_start, ('戌','亥'))
    kong_palaces = list({DIZHI_TO_PALACE[z] for z in kong_pair if z in DIZHI_TO_PALACE})
    return kong_pair, kong_palaces


def get_ma_xing(hour_zhi):
    """计算驿马星所在地支及宫位（以时支为基准，口诀：申子辰马在寅 / 寅午戌马在申 / 巳酉丑马在亥 / 亥卯未马在巳）"""
    ma_zhi = MA_MAP.get(hour_zhi, '寅')
    ma_palace = DIZHI_TO_PALACE.get(ma_zhi, 8)
    return ma_zhi, ma_palace


def solve(year_gz, month_gz, day_gz, hour_gz, jieqi, dun, bureau):
    """完整排盘，返回结构化数据"""
    hour_gan = hour_gz[0]
    hour_zhi = hour_gz[1]

    # ── 1. 旬首干 ───────────────────────────────────────────────
    xun_shou_gan = get_xun_shou_gan(hour_gan, hour_zhi)

    # ── 2. 地盘 ─────────────────────────────────────────────────
    di_pan = get_di_pan(dun, bureau)

    # 旬首干在地盘的宫位
    xun_shou_pos = None
    for p, g in di_pan.items():
        if g == xun_shou_gan:
            xun_shou_pos = p
            break
    if xun_shou_pos is None:
        xun_shou_pos = 1

    # 时干在地盘的宫位
    hour_gan_pos = None
    for p, g in di_pan.items():
        if g == hour_gan:
            hour_gan_pos = p
            break
    if hour_gan_pos is None:
        hour_gan_pos = xun_shou_pos

    # ── 3. 值符信息 ─────────────────────────────────────────────
    zhi_fu_star = STARS_BY_PALACE.get(xun_shou_pos, '天蓬')

    # ── 4. 天盘（"值符随时干"）──────────────────────────────────
    hv_stems, jigan_stems = calc_heaven_plate(di_pan, dun, xun_shou_pos, hour_gan_pos)

    # 天盘星（随天盘干，干来自地盘哪个宫，那个宫的固定星跟来）
    hv_stars = {}
    hv_stars_jigan = {}  # 寄星：天禽跟随天芮
    for p in range(1, 10):
        g = hv_stems.get(p, '')
        if g:
            orig_p_list = [k for k, v in di_pan.items() if v == g]
            if orig_p_list:
                hv_stars[p] = STARS_BY_PALACE.get(orig_p_list[0], '')
            else:
                hv_stars[p] = ''
        else:
            hv_stars[p] = ''
        # 天禽星跟随天芮星，寄干所在宫即为天禽落宫
        if p in jigan_stems and jigan_stems[p]:
            hv_stars_jigan[p] = '天禽'

    # 天盘值符落宫 = 时干宫（值符转到时干所在宫）
    heaven_zf_palace = hour_gan_pos

    # ── 5. 八门（"值使随时支"）──────────────────────────────────
    palace_doors, zhi_shi_door, zhi_shi_pos = calc_doors(
        di_pan, dun, xun_shou_pos, hour_gan, hour_zhi
    )

    # ── 6. 八神（"小值符随大值符"）──────────────────────────────
    palace_gods = calc_gods(dun, heaven_zf_palace)            # 天盘八神
    earth_gods  = calc_earth_gods(dun, xun_shou_pos)          # 地盘八神

    # ── 7. 旬空、驿马 ───────────────────────────────────────────
    kong_pair, kong_palaces = get_xun_kong(hour_gan, hour_zhi)
    ma_zhi, ma_palace = get_ma_xing(hour_zhi)

    # ── 8. 地盘寄干（坤2宫寄中5宫的地盘干）──────────────────────
    earth_jigan = {2: di_pan.get(5, '')}

    return {
        'chart_info': {
            'time': f'{year_gz}年 {month_gz}月 {day_gz}日 {hour_gz}时',
            'jieqi': jieqi,
            'dun': dun,
            'bureau': f'{dun}遁{bureau}局',
            'xun_shou_gan': xun_shou_gan,
            'zhi_fu_star': zhi_fu_star,
            'zhi_fu_pos': xun_shou_pos,       # 值符原始宫（旬首干所在宫）
            'zhi_fu_heaven_pos': heaven_zf_palace,  # 天盘值符落宫（=时干宫）
            'zhi_shi_door': zhi_shi_door,
            'zhi_shi_pos': zhi_shi_pos,
            'kong_pair': kong_pair,
            'kong_palaces': kong_palaces,
            'ma_zhi': ma_zhi,
            'ma_palace': ma_palace,
        },
        'di_pan': di_pan,
        'earth_jigan': earth_jigan,        # 地盘寄干 {2: '乙'}
        'hv_stems': hv_stems,
        'jigan_stems': jigan_stems,         # 天盘寄干（天芮落宫=天禽带5宫地盘干）
        'hv_stars': hv_stars,
        'hv_stars_jigan': hv_stars_jigan,   # 寄星：天禽跟随天芮 {3: '天禽'}
        'palace_doors': palace_doors,
        'palace_gods': palace_gods,              # 天盘八神
        'earth_gods': earth_gods,                # 地盘八神（从旬首宫起）
    }


if __name__ == '__main__':
    print('=' * 60)
    print('=== 验证: 阴遁7局 辛丑时（qm.png参考案例）===')
    # qm.png: 2019-07-29 辛丑时 阴遁7局 大暑
    # 地盘期望: {1:'丁',2:'癸',3:'壬',4:'辛',5:'庚',6:'己',7:'戊',8:'乙',9:'丙'}
    # 八门期望（地盘）: {1:'景',2:'生',3:'惊',4:'开',6:'杜',7:'伤',8:'死',9:'休'}
    # 注：qm.png八门是按地盘干走，而非按规则文档的值使法——需确认
    r1 = solve('己亥', '辛未', '丁卯', '辛丑', '大暑', '阴', 7)
    print('地盘:', {k: v for k, v in sorted(r1['di_pan'].items())})
    print('天盘:', {k: v for k, v in sorted(r1['hv_stems'].items())})
    print('八门:', {k: v for k, v in sorted(r1['palace_doors'].items()) if v})
    print('八神:', {k: v for k, v in sorted(r1['palace_gods'].items()) if k != 5})
    print('旬首干:', r1['chart_info']['xun_shou_gan'])
    print('值符:', r1['chart_info']['zhi_fu_star'], '原宫:', r1['chart_info']['zhi_fu_pos'])
    print('值符天盘落宫:', r1['chart_info']['zhi_fu_heaven_pos'])
    print('值使:', r1['chart_info']['zhi_shi_door'], '落宫:', r1['chart_info']['zhi_shi_pos'])
    print()

    # 验证地盘
    exp_dp = {1:'丁',2:'癸',3:'壬',4:'辛',5:'庚',6:'己',7:'戊',8:'乙',9:'丙'}
    dp_ok = all(r1['di_pan'].get(k)==v for k,v in exp_dp.items())
    print(f'地盘验证: {"OK" if dp_ok else "NG"}')
    if not dp_ok:
        for k, v in exp_dp.items():
            got = r1['di_pan'].get(k, '?')
            if got != v:
                print(f'  宫{k}: 期望{v} 得到{got}')

    print()
    print('=== 当前排盘（2026-06-06 22:01 亥时 芒种上元 阳遁6局）===')
    r2 = solve('丙午', '甲午', '辛亥', '己亥', '芒种', '阳', 6)
    print('地盘:', {k: v for k, v in sorted(r2['di_pan'].items())})
    print('天盘:', {k: v for k, v in sorted(r2['hv_stems'].items())})
    print('八门:', {k: v for k, v in sorted(r2['palace_doors'].items()) if v})
    print('八神:', {k: v for k, v in sorted(r2['palace_gods'].items()) if k != 5})
    print('旬首干:', r2['chart_info']['xun_shou_gan'])
    print('值符:', r2['chart_info']['zhi_fu_star'], '落宫:', r2['chart_info']['zhi_fu_heaven_pos'])
    print('值使:', r2['chart_info']['zhi_shi_door'], '落宫:', r2['chart_info']['zhi_shi_pos'])
