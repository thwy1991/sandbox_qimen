# -*- coding: utf-8 -*-
"""
奇门语料库工具脚本
1. 生成任意时间的排盘 JSON 模板
2. 将 JSON 记录转换为 JSONL 格式
"""
import json
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generate_qimen_image import get_all_gz, get_bureau_info
from qimen_engine_v2 import solve

# 宫位方向映射
PALACE_DIR = {1: "坎", 2: "坤", 3: "震", 4: "巽", 5: "中", 6: "乾", 7: "兑", 8: "艮", 9: "离"}


def generate_pan_template(dt, market="", direction="", target=""):
    """生成指定时间的奇门盘语料模板"""
    year_gz, month_gz, day_gz, hour_gz = get_all_gz(dt)
    jieqi, dun, bureau_num, yuan = get_bureau_info(dt)
    bureau_str = f"{dun}遁{bureau_num}局"

    result = solve(year_gz, month_gz, day_gz, hour_gz, jieqi, dun, bureau_num)
    info = result["chart_info"]

    # 构建 pan_summary
    palaces = []
    for p in [1, 2, 3, 4, 6, 7, 8, 9]:
        star_name = result["hv_stars"].get(str(p), "")
        if str(p) in result.get("hv_stars_jigan", {}):
            star_name += "+天禽"
        notes = []
        if p in info["kong_palaces"]:
            notes.append("空亡")
        if p == info["zhi_shi_pos"]:
            notes.append("值使宫")
        if p == info["zhi_fu_heaven_pos"]:
            notes.append("天盘值符宫")
        if p == info["ma_palace"]:
            notes.append("驿马")

        palaces.append({
            "palace": p,
            "dir": PALACE_DIR.get(p, ""),
            "di_gan": result["di_pan"].get(str(p), ""),
            "tian_gan": result["hv_stems"].get(str(p), ""),
            "star": star_name,
            "door": result["palace_doors"].get(str(p), ""),
            "god": result["palace_gods"].get(str(p), ""),
            "jigan": result["jigan_stems"].get(str(p)),
            "note": "，".join(notes)
        })

    template = {
        "id": f"qimen_{dt.strftime('%Y%m%d_%H%M')}",
        "datetime": dt.strftime("%Y-%m-%dT%H:%M:%S"),
        "pan": {
            "chart_info": {
                "time": f"{year_gz}年 {month_gz}月 {day_gz}日 {hour_gz}时",
                "jieqi": jieqi,
                "dun": dun,
                "bureau": bureau_str,
                "yuan": yuan,
                "xun_shou_gan": info["xun_shou_gan"],
                "zhi_fu_star": info["zhi_fu_star"],
                "zhi_fu_pos": info["zhi_fu_pos"],
                "zhi_fu_heaven_pos": info["zhi_fu_heaven_pos"],
                "zhi_shi_door": info["zhi_shi_door"],
                "zhi_shi_pos": info["zhi_shi_pos"],
                "kong_pair": info["kong_pair"],
                "kong_palaces": info["kong_palaces"],
                "ma_zhi": info["ma_zhi"],
                "ma_palace": info["ma_palace"]
            },
            "di_pan": {str(k): v for k, v in result["di_pan"].items()},
            "earth_jigan": {str(k): v for k, v in result["earth_jigan"].items()},
            "hv_stems": {str(k): v for k, v in result["hv_stems"].items()},
            "jigan_stems": {str(k): v for k, v in result.get("jigan_stems", {}).items()},
            "hv_stars": {str(k): v for k, v in result["hv_stars"].items()},
            "hv_stars_jigan": {str(k): v for k, v in result.get("hv_stars_jigan", {}).items()},
            "palace_doors": {str(k): v for k, v in result["palace_doors"].items()},
            "palace_gods": {str(k): v for k, v in result["palace_gods"].items()},
            "earth_gods": {str(k): v for k, v in result["earth_gods"].items()}
        },
        "pan_summary": {
            "dun_type": f"{dun}遁",
            "bureau_num": bureau_num,
            "zhi_fu": {"star": info["zhi_fu_star"], "origin_palace": info["zhi_fu_pos"], "heaven_palace": info["zhi_fu_heaven_pos"]},
            "zhi_shi": {"door": info["zhi_shi_door"], "palace": info["zhi_shi_pos"]},
            "kong_palaces": info["kong_palaces"],
            "ma_palace": info["ma_palace"],
            "palaces": palaces
        },
        "context": {
            "market": market,
            "time_range": "",
            "direction": direction,
            "specific_target": target,
            "notes": ""
        },
        "analysis": "（请填写分析过程）",
        "outcome": {
            "predicted": "",
            "actual": "",
            "accuracy": "",
            "key_turning_point": "",
            "deviation_reason": ""
        },
        "insights": "（请填写心得感悟）",
        "tags": [],
        "rating": 0,
        "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    }

    return template


def json_to_jsonl(json_file, jsonl_file):
    """将单个 JSON 记录追加到 JSONL 文件"""
    with open(json_file, "r", encoding="utf-8") as f:
        record = json.load(f)

    with open(jsonl_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"已追加到 {jsonl_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="奇门语料库工具")
    parser.add_argument("action", choices=["gen", "convert"], help="gen=生成模板, convert=转JSONL")
    parser.add_argument("--datetime", type=str, help="日期时间 YYYY-MM-DD HH:MM")
    parser.add_argument("--market", type=str, default="", help="分析市场")
    parser.add_argument("--target", type=str, default="", help="具体标的")
    parser.add_argument("--json", type=str, help="输入的JSON文件路径")
    parser.add_argument("--jsonl", type=str, help="输出的JSONL文件路径")
    parser.add_argument("--output", type=str, help="模板输出路径")

    args = parser.parse_args()

    if args.action == "gen":
        if not args.datetime:
            print("请指定 --datetime 'YYYY-MM-DD HH:MM'")
            sys.exit(1)

        dt = datetime.strptime(args.datetime, "%Y-%m-%d %H:%M")
        template = generate_pan_template(dt, market=args.market, target=args.target)

        output_path = args.output or f"corpus_template_{dt.strftime('%Y%m%d_%H%M')}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(template, f, ensure_ascii=False, indent=2)

        print(f"模板已生成: {output_path}")
        print(f"\n=== 盘面速览 ===")
        info = template["pan"]["chart_info"]
        print(f"时间: {info['time']}")
        print(f"节气: {info['jieqi']} {info['bureau']} ({info['yuan']})")
        print(f"值符: {info['zhi_fu_star']}({info['zhi_fu_pos']}宫) → 天盘落{info['zhi_fu_heaven_pos']}宫")
        print(f"值使: {info['zhi_shi_door']} 落{info['zhi_shi_pos']}宫")
        print(f"旬空: {info['kong_pair']} → {info['kong_palaces']}宫")
        print(f"驿马: {info['ma_zhi']} → {info['ma_palace']}宫")

    elif args.action == "convert":
        if not args.json or not args.jsonl:
            print("请指定 --json 输入文件 和 --jsonl 输出文件")
            sys.exit(1)
        json_to_jsonl(args.json, args.jsonl)
