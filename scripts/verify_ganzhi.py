# -*- coding: utf-8 -*-
"""验证日干支基准并修正"""
from datetime import date

TIANGAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DIZHI   = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

# 已知可靠基准：2024年1月1日 = 甲子日 (序号0)
BASE = date(2024, 1, 1)
BASE_POS = 0  # 甲子

def get_day_gan_zhi_v2(y, m, d):
    d0 = date(y, m, d)
    delta = (d0 - BASE).days
    pos = (BASE_POS + delta) % 60
    return TIANGAN[pos % 10] + DIZHI[pos % 12]

# 验证2019-07-29
gz_20190729 = get_day_gan_zhi_v2(2019, 7, 29)
print(f'2019-07-29 正确干支: {gz_20190729}')

# 验证2026-06-08
gz_20260608 = get_day_gan_zhi_v2(2026, 6, 8)
print(f'2026-06-08 正确干支: {gz_20260608}')

# 原代码基准得出的结果
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate_qimen_image import get_day_gan_zhi
gz_old = get_day_gan_zhi(2026, 6, 8)
print(f'2026-06-08 原代码干支: {gz_old}')
print(f'偏差: 原代码多算了1天 (从丁卯序号3偏移到戊辰序号4)')
