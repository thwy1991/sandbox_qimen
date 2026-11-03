# -*- coding: utf-8 -*-
"""快速生成指定时间的奇门盘图片"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from generate_qimen_image import get_all_gz, get_bureau_info, draw_qimen_chart
from qimen_engine_v2 import solve


def gen_qimen_image(dt, output_path=None):
    """为指定 datetime 生成奇门盘 PNG 图片"""
    year_gz, month_gz, day_gz, hour_gz = get_all_gz(dt)
    jieqi, dun, bureau_num, yuan = get_bureau_info(dt)

    result = solve(year_gz, month_gz, day_gz, hour_gz, jieqi, dun, bureau_num)

    if output_path is None:
        output_path = f"output/qimen_{dt.strftime('%Y%m%d_%H%M')}.png"

    draw_qimen_chart(
        result,
        output_path,
        dt_str=dt.strftime('%Y年%m月%d日 %H:%M'),
        jieqi=jieqi,
        dun=dun,
        bureau_num=bureau_num,
        yuan=yuan
    )
    print(f"图片已生成: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scripts/gen_image.py 'YYYY-MM-DD HH:MM' [output_path]")
        print("示例: python scripts/gen_image.py '2026-06-08 10:00'")
        sys.exit(1)

    dt = datetime.strptime(sys.argv[1], "%Y-%m-%d %H:%M")
    out = sys.argv[2] if len(sys.argv) > 2 else None
    gen_qimen_image(dt, out)
