# -*- coding: utf-8 -*-
"""验证八门修复后的三个案例"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from qimen_engine_v2 import DOOR_NUM_SEQ, DOOR_NUM_RSEQ, DOORS_BY_PALACE, jiazi_pos

print('更新后的路径:')
print(f'  DOOR_NUM_SEQ  = {DOOR_NUM_SEQ}')
print(f'  DOOR_NUM_RSEQ = {DOOR_NUM_RSEQ}')
print()

# 验证案例1: 甲戌旬, 庚辰时, 旬首宫=7
print('=== 文档案例1: 阳遁 甲戌->庚辰 ===')
steps1 = jiazi_pos('庚','辰') - 10
path1 = DOOR_NUM_SEQ
si1 = path1.index(7)
result1 = path1[(si1 + steps1) % len(path1)]
ok1 = 'OK' if result1 == 4 else 'NG'
print(f'  步数={steps1}, 起点=7索引{si1}, 结果={result1}宫 (期望4) [{ok1}]')

# 验证案例2: 甲子旬, 丁卯时, 旬首宫=1, 阴遁
print('=== 文档案例2: 阴遁 甲子->丁卯 ===')
steps2 = jiazi_pos('丁','卯') - 0
path2 = DOOR_NUM_RSEQ
si2 = path2.index(1)
result2 = path2[(si2 + steps2) % len(path2)]
ok2 = 'OK' if result2 == 7 else 'NG'
print(f'  步数={steps2}, 起点=1索引{si2}, 结果={result2}宫 (期望7) [{ok2}]')

# 验证案例3: 甲寅旬, 癸亥时, 旬首宫=2
print('=== 案例3: 阳遁 甲寅->癸亥 (用户反馈bug) ===')
steps3 = jiazi_pos('癸','亥') - 50
path3 = DOOR_NUM_SEQ
si3 = path3.index(2)
result3 = path3[(si3 + steps3) % len(path3)]
ok3 = 'OK' if result3 == 2 else 'NG'
print(f'  步数={steps3}, 起点=2索引{si3}, 结果={result3}宫 (期望2) [{ok3}]')
print()

# 手动步进验证
print('=== 逐位步进验证 (含5宫路径) ===')
for i in range(steps3 + 1):
    cur = path3[(si3 + i) % len(path3)]
    marker = ''
    if i == 0:
        marker = '<- 旬首甲寅'
    elif i == steps3:
        marker = '<- 时柱癸亥'
    print(f'  第{i}步: {cur}宫 {marker}')

print()
print('全部通过!' if (ok1=='OK' and ok2=='OK' and ok3=='OK') else '有失败案例!')
