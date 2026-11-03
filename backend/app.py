# -*- coding: utf-8 -*-
"""
奇门遁甲排盘后端API服务

基于 qimen_engine_v2.py 引擎，提供RESTful API供微信小程序调用。
"""

import os
import sys
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from qimen_engine_v2 import solve as solve_qimen, get_xun_shou_gan, get_xun_kong, get_ma_xing
from generate_qimen_image import get_all_gz, get_bureau_info, get_hour_zhi

app = Flask(__name__)
CORS(app)

# ── 常量 ──────────────────────────────────────────────────────
TIANGAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DIZHI   = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

# 洛书宫位布局
PALACE_TO_RC = {
    4: (0, 0), 9: (0, 1), 2: (0, 2),
    3: (1, 0), 5: (1, 1), 7: (1, 2),
    8: (2, 0), 1: (2, 1), 6: (2, 2),
}

PALACE_NAME = {
    1: '坎', 2: '坤', 3: '震', 4: '巽',
    5: '中', 6: '乾', 7: '兑', 8: '艮', 9: '离'
}

# 旬首完整名称
XUN_FULL = {
    '戊': '甲子戊', '己': '甲戌己', '庚': '甲申庚',
    '辛': '甲午辛', '壬': '甲辰壬', '癸': '甲寅癸'
}


@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'service': 'qimen-api'})


@app.route('/api/qimen/chart', methods=['POST'])
def get_chart():
    """
    排盘接口

    请求参数 (JSON):
    {
        "year": 2026,
        "month": 6,
        "day": 6,
        "hour": 22,
        "minute": 5
    }

    返回排盘完整数据。
    """
    try:
        data = request.get_json(force=True)
        year = int(data.get('year', datetime.now().year))
        month = int(data.get('month', datetime.now().month))
        day = int(data.get('day', datetime.now().day))
        hour = int(data.get('hour', datetime.now().hour))
        minute = int(data.get('minute', datetime.now().minute))

        # 构造datetime
        dt = datetime(year, month, day, hour, minute)

        # 计算四柱
        year_gz, month_gz, day_gz, hour_gz = get_all_gz(dt)

        # 计算节气和局数
        jieqi_name, dun, bureau_num, yuan = get_bureau_info(dt)

        # 排盘
        result = solve_qimen(year_gz, month_gz, day_gz, hour_gz,
                             jieqi_name, dun, bureau_num)

        # 构造返回数据
        ci = result['chart_info']
        response = {
            'success': True,
            'datetime': {
                'year': year,
                'month': month,
                'day': day,
                'hour': hour,
                'minute': minute,
                'str': dt.strftime('%Y年%m月%d日 %H:%M')
            },
            'sizhu': {
                'year': year_gz,
                'month': month_gz,
                'day': day_gz,
                'hour': hour_gz,
                'str': f'{year_gz}年 {month_gz}月 {day_gz}日 {hour_gz}时'
            },
            'jieqi': jieqi_name,
            'yuan': yuan,
            'dun': dun,
            'bureau': bureau_num,
            'bureau_str': f'{dun}遁{bureau_num}局',
            'xun_shou_gan': ci['xun_shou_gan'],
            'xun_shou_full': XUN_FULL.get(ci['xun_shou_gan'], ci['xun_shou_gan']),
            'zhi_fu_star': ci['zhi_fu_star'],
            'zhi_fu_pos': ci['zhi_fu_pos'],
            'zhi_fu_heaven_pos': ci['zhi_fu_heaven_pos'],
            'zhi_shi_door': ci['zhi_shi_door'],
            'zhi_shi_pos': ci['zhi_shi_pos'],
            'kong_pair': list(ci['kong_pair']),
            'kong_palaces': ci['kong_palaces'],
            'ma_zhi': ci['ma_zhi'],
            'ma_palace': ci['ma_palace'],
            'di_pan': {str(k): v for k, v in sorted(result['di_pan'].items())},
            'earth_jigan': {str(k): v for k, v in result.get('earth_jigan', {}).items()},
            'hv_stems': {str(k): v for k, v in sorted(result['hv_stems'].items())},
            'jigan_stems': {str(k): v for k, v in result.get('jigan_stems', {}).items()},
            'hv_stars': {str(k): v for k, v in sorted(result['hv_stars'].items())},
            'hv_stars_jigan': {str(k): v for k, v in result.get('hv_stars_jigan', {}).items()},
            'palace_doors': {str(k): v for k, v in sorted(result['palace_doors'].items())},
            'palace_gods': {str(k): v for k, v in sorted(result['palace_gods'].items())},
            'earth_gods': {str(k): v for k, v in sorted(result['earth_gods'].items())},
            # 九宫格数据（按洛书布局排好序，前端直接渲染）
            'palaces': _build_palaces_data(result, ci)
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/qimen/now', methods=['GET'])
def get_now_chart():
    """获取当前时间的排盘"""
    now = datetime.now()
    data = {
        'year': now.year,
        'month': now.month,
        'day': now.day,
        'hour': now.hour,
        'minute': now.minute
    }
    # 复用 get_chart 逻辑
    import json
    with app.test_request_context('/api/qimen/chart', method='POST', json=data):
        return get_chart()


def _build_palaces_data(result, ci):
    """构建九宫格数据，按洛书布局排列"""
    dp = result['di_pan']
    hv = result['hv_stems']
    hs = result['hv_stars']
    pd_doors = result['palace_doors']
    pg = result['palace_gods']
    eg = result['earth_gods']
    kong_palaces = ci.get('kong_palaces', [])
    ma_palace = ci.get('ma_palace', 0)
    zhi_fu_pos = ci.get('zhi_fu_heaven_pos', ci.get('zhi_fu_pos', 0))
    if zhi_fu_pos == 5:
        zhi_fu_pos = 2
    zhi_shi_pos = ci.get('zhi_shi_pos', 0)
    jigan_stems = result.get('jigan_stems', {})
    hv_stars_jigan = result.get('hv_stars_jigan', {})
    earth_jigan = result.get('earth_jigan', {})

    palaces = []
    for palace in range(1, 10):
        row, col = PALACE_TO_RC[palace]
        p_data = {
            'palace': palace,
            'row': row,
            'col': col,
            'name': PALACE_NAME[palace],
            'di_pan_stem': dp.get(palace, ''),
            'hv_stem': hv.get(palace, ''),
            'hv_star': hs.get(palace, ''),
            'door': pd_doors.get(palace, ''),
            'god': pg.get(palace, ''),
            'earth_god': eg.get(palace, ''),
            'is_center': palace == 5,
            'is_zhi_fu': palace == zhi_fu_pos,
            'is_zhi_shi': palace == zhi_shi_pos,
            'is_kong': palace in kong_palaces,
            'is_ma': palace == ma_palace,
            'jigan_stem': jigan_stems.get(palace, ''),
            'jigan_star': hv_stars_jigan.get(palace, ''),
            'earth_jigan': earth_jigan.get(palace, ''),
        }
        palaces.append(p_data)

    return palaces


@app.route('/api/hour_zhi', methods=['GET'])
def get_hour_zhi_api():
    """根据小时获取时辰地支"""
    hour = int(request.args.get('hour', 0))
    zhi = get_hour_zhi(hour)
    return jsonify({'hour': hour, 'zhi': zhi})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
