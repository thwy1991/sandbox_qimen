# 奇门实战分析语料库 JSON Schema 规范

## 概述

本规范定义了奇门遁甲实战分析语料库的 JSON 数据格式，用于记录奇门盘面数据及其对应的分析心得，为后续 AI 训练或 RAG 检索提供结构化语料。

## 文件格式

- **格式**: JSONL（每行一个完整的 JSON 对象）
- **编码**: UTF-8
- **命名**: `corpus_*.jsonl`

---

## 字段定义

### 顶层结构

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一标识，格式：`qimen_{YYYYMMDD}_{HHMM}` |
| `datetime` | string | ✅ | 排盘时间 ISO 8601，如 `"2026-06-10T14:00:00"` |
| `pan` | object | ✅ | 完整奇门排盘数据（见 pan 子结构） |
| `context` | object | ✅ | 分析场景/上下文（见 context 子结构） |
| `analysis` | string | ✅ | 当时的完整分析记录 |
| `outcome` | object | ✅ | 预测与结果对照（见 outcome 子结构） |
| `insights` | string | ✅ | 心得感悟和经验总结 |
| `tags` | array[string] | ❌ | 标签，用于分类检索 |
| `rating` | integer | ❌ | 自评准确度 1-5（5=完全准确） |
| `created_at` | string | ❌ | 记录创建时间 |

---

### `pan` - 奇门排盘数据

```json
{
  "chart_info": {
    "time": "年干支 月干支 日干支 时干支（中文格式）",
    "jieqi": "节气名",
    "dun": "阳｜阴",
    "bureau": "X遁X局",
    "yuan": "上元｜中元｜下元",
    "xun_shou_gan": "旬首干（戊～癸）",
    "zhi_fu_star": "值符星名",
    "zhi_fu_pos": "值符原始宫位(1-9)",
    "zhi_fu_heaven_pos": "天盘值符落宫(1-9)",
    "zhi_shi_door": "值使门名",
    "zhi_shi_pos": "值使落宫(1-9)",
    "kong_pair": ["空亡地支1", "空亡地支2"],
    "kong_palaces": [空亡宫位1, 空亡宫位2],
    "ma_zhi": "驿马地支",
    "ma_palace": "驿马宫位(1-9)"
  },
  "di_pan": { "1":"干", ..., "9":"干" },
  "earth_jigan": { "2":"寄干" },
  "hv_stems": { "1":"天盘干", ..., "9":"天盘干" },
  "jigan_stems": { "宫":"寄干" },
  "hv_stars": { "1":"天盘星", ..., "9":"天盘星" },
  "hv_stars_jigan": { "宫":"天禽" },
  "palace_doors": { "1":"门", ..., "9":"门" },
  "palace_gods": { "1":"天盘神", ..., "9":"天盘神" },
  "earth_gods": { "1":"地盘神", ..., "9":"地盘神" }
}
```

**宫位数字说明**:
- `1` 坎（北） `2` 坤（西南） `3` 震（东） `4` 巽（东南）
- `5` 中宫（寄坤2） `6` 乾（西北） `7` 兑（西） `8` 艮（东北） `9` 离（南）

---

### `pan_summary` - 盘面结构化摘要（可选，便于检索）

```json
{
  "dun_type": "阳遁",
  "bureau_num": 3,
  "zhi_fu_star_palace": 8,
  "zhi_shi_door_palace": 4,
  "kong_palaces": [2, 7],
  "ma_palace": 4,
  "star_keys": [
    {"palace": 8, "star": "天辅", "god": "值符", "door": "生门", "di_gan": "癸", "tian_gan": "己"},
    ...所有9宫
  ]
}
```

---

### `context` - 分析场景

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `market` | string | ✅ | 分析市场，如 `"A股大盘"`, `"金属期货"`, `"金融期货"`, `"上证指数"` |
| `time_range` | string | ❌ | 分析覆盖时间段，如 `"14:00-15:00"` |
| `direction` | string | ❌ | 分析方向，如 `"大盘走势"`, `"个股涨跌"`, `"板块轮动"` |
| `specific_target` | string | ❌ | 具体标的，如 `"沪银2506"`, `"沪深300"` |
| `notes` | string | ❌ | 场景备注 |

---

### `outcome` - 预测与结果对照

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `predicted` | string | ✅ | 当时预测的判断，如 `"先冲高后回落，偏空"` |
| `actual` | string | ✅ | 实际走势，如 `"14:05冲高0.8%，14:20开始单边下行"` |
| `accuracy` | string | ✅ | 准确度评价，如 `"准确"`, `"基本准确"`, `"偏误"`, `"完全错误"` |
| `key_turning_point` | string | ❌ | 关键转折时间点 |
| `deviation_reason` | string | ❌ | 偏差原因分析 |

---

### `insights` - 心得感悟（核心字段）

记录内容建议包含：
- 本次分析中「独特的发现」
- 哪些格局/信号被验证有效
- 哪些信号被市场否定
- 与历史案例的关联
- 对规则/口诀的新理解

---

## 完整 JSON 示例

```json
{
  "id": "qimen_20260610_1400",
  "datetime": "2026-06-10T14:00:00",
  "pan": {
    "chart_info": {
      "time": "丙午年 甲午月 乙卯日 癸未时",
      "jieqi": "芒种",
      "dun": "阳",
      "bureau": "阳遁3局",
      "yuan": "中元",
      "xun_shou_gan": "己",
      "zhi_fu_star": "天辅",
      "zhi_fu_pos": 4,
      "zhi_fu_heaven_pos": 8,
      "zhi_shi_door": "杜门",
      "zhi_shi_pos": 4,
      "kong_pair": ["申", "酉"],
      "kong_palaces": [2, 7],
      "ma_zhi": "巳",
      "ma_palace": 4
    },
    "...": "其余盘面字段见实际生成"
  },
  "context": {
    "market": "A股大盘",
    "time_range": "14:00-15:00",
    "direction": "大盘走势",
    "notes": ""
  },
  "analysis": "（在此记录当时的完整分析文字）",
  "outcome": {
    "predicted": "",
    "actual": "",
    "accuracy": "",
    "key_turning_point": "",
    "deviation_reason": ""
  },
  "insights": "（在此记录心得感悟）",
  "tags": ["阳遁", "值符空亡", "驿马临值使"],
  "rating": 0,
  "created_at": "2026-06-10T20:48:00"
}
```

---

## 使用说明

### 1. 快速创建新记录

复制模板文件 `corpus_template.jsonl`，填写 `analysis`、`outcome`、`insights` 即可。

### 2. 标签体系建议

```
# 格局类
"值符空亡", "值使反吟", "伏吟局", "返吟局", "五不遇时", "天显时格"

# 宫位类
"值符落艮", "开门临九天", "死门值使"

# 市场类
"A股", "期货", "外汇", "个股"

# 准确度类
"准确", "偏误", "待验证"
```

### 3. 检索维度

- 按值符星+落宫检索相似盘
- 按旬空宫位检索
- 按节气+局数检索
- 按标签分类检索
- 按准确度筛选高信度案例

---

**最后更新**: 2026-06-10
