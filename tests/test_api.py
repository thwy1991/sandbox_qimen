# -*- coding: utf-8 -*-
"""测试API服务"""
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app

with app.test_client() as c:
    # 测试健康检查
    r = c.get('/api/health')
    print('=== 健康检查 ===')
    print(r.get_json())

    # 测试排盘
    r2 = c.post('/api/qimen/chart', json={
        'year': 2026, 'month': 6, 'day': 6, 'hour': 22, 'minute': 5
    })
    data = r2.get_json()
    print()
    print('=== 排盘结果 ===')
    print('成功:', data['success'])
    print('时间:', data['datetime']['str'])
    print('四柱:', data['sizhu']['str'])
    print('节气:', data['jieqi'], data['yuan'], data['bureau_str'])
    print('旬首:', data['xun_shou_full'])
    print('值符:', data['zhi_fu_star'], '落', data['zhi_fu_heaven_pos'], '宫')
    print('值使:', data['zhi_shi_door'], '落', data['zhi_shi_pos'], '宫')
    print('旬空:', data['kong_pair'], '宫位', data['kong_palaces'])
    print('驿马:', data['ma_zhi'], '宫', data['ma_palace'])
    print()
    print('九宫格数据:')
    for p in data['palaces']:
        palace = p['palace']
        name = p['name']
        god = p['god']
        star = p['hv_star']
        hv_stem = p['hv_stem']
        door = p['door']
        dp_stem = p['di_pan_stem']
        print(f'  {palace}宫({name}): 神={god} 星={star} 天干={hv_stem} 门={door} 地干={dp_stem}')

    # 测试当前时间排盘
    r3 = c.get('/api/qimen/now')
    data3 = r3.get_json()
    print()
    print('=== 当前时间排盘 ===')
    print('成功:', data3['success'])
    print('时间:', data3['datetime']['str'])
    print('四柱:', data3['sizhu']['str'])
    print('局数:', data3['bureau_str'])
