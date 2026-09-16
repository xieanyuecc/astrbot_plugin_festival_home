# -*- coding: utf-8 -*-
"""核心逻辑测试（不依赖 AstrBot runtime）

跑法：python sim_test.py
全部通过输出「35/35 全过」（数量随用例增减）。
"""
import sys
from datetime import date

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from festival.home import (
    DAY_CARDS,
    DAY_DAY_CARDS,
    EVE_CARDS,
    QUIET_CARDS,
    ZHONGQIU,
    _draw_piles,
    day_part,
    moon_text,
    scene_text,
    zhongqiu_span,
)

PASS = 0
FAIL = 0


def check(name: str, cond: bool, detail: str = ""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAIL += 1
        print(f"  ✗ {name}  {detail}")


print("── 时段划分 ──")
for h, want in [(4, "predawn"), (5, "morning"), (10, "morning"), (11, "noon"),
                (16, "noon"), (17, "evening"), (20, "evening"), (21, "night"),
                (1, "night"), (0, "night"), (2, "predawn")]:
    check(f"{h} 点 → {want}", day_part(h) == want, f"实际 {day_part(h)}")

print("── 中秋日期表 ──")
check("2026-2035 十年全有", all(y in ZHONGQIU for y in range(2026, 2036)))
check("2026 中秋是 9/25", zhongqiu_span(2026)[0] == date(2026, 9, 25))
check("2028 中秋是 10/3", zhongqiu_span(2028)[0] == date(2028, 10, 3))
check("2035 中秋是 9/16", zhongqiu_span(2035)[0] == date(2035, 9, 16))

print("── 街景：中秋正日 2026-09-25 ──")
noon = scene_text(date(2026, 9, 25), 12)
check("白天（12 点）出正日白天卡", noon in DAY_DAY_CARDS, noon[:20])
_eve_deck = scene_text(date(2026, 9, 25), 19)
check("傍晚（19 点）出天台/月亮卡", _eve_deck in DAY_CARDS, _eve_deck[:20])
_night = scene_text(date(2026, 9, 25), 23)
check("深夜（23 点）仍出正日夜卡", _night in DAY_CARDS, _night[:20])
_predawn = scene_text(date(2026, 9, 25), 3)
check("凌晨（3 点）仍出正日夜卡（还没睡的天台）", _predawn in DAY_CARDS, _predawn[:20])

print("── 街景：前夜 / 追月 / 节前节后 ──")
eve = scene_text(date(2026, 9, 24), 20)
check("前夜（9/24）出八月十四卡", eve in EVE_CARDS, eve[:20])
d2 = scene_text(date(2026, 9, 26), 20)
check("追月（9/26）出十六卡", "追月" in d2 or "柚子" in d2, d2[:20])
near_b = scene_text(date(2026, 9, 22), 15)
check("节前（9/22）超市月饼堆头", "月饼堆头" in near_b, near_b[:20])
near_a = scene_text(date(2026, 9, 28), 15)
check("节后（9/28）月饼五折", "五折" in near_a, near_a[:20])
far = scene_text(date(2026, 9, 5), 15)
check("远离节日（9/5）回普通街景", "今天不是节" in far, far[:20])

print("── 街景：普通日五时段 ──")
for part, hour in [("morning", 8), ("noon", 13), ("evening", 18), ("night", 22), ("predawn", 3)]:
    _draw_piles.pop(f"quiet:{part}", None)  # 清牌堆，保证能抽到本时段卡
    t = scene_text(date(2026, 6, 10), hour)
    check(f"{part}（{hour} 点）出对应卡", t in QUIET_CARDS[part], t[:20])

print("── 洗牌制：一轮内每张必出且只出一次 ──")
_draw_piles.clear()
drawn = [scene_text(date(2026, 6, 10), 8) for _ in range(len(QUIET_CARDS["morning"]))]
check("晨卡 4 张抽 4 次无重复", len(set(drawn)) == len(QUIET_CARDS["morning"]), str(len(set(drawn))))
check("恰好是整套晨卡", set(drawn) == set(QUIET_CARDS["morning"]))
_draw_piles.clear()
drawn_eve = [scene_text(date(2026, 9, 24), 20) for _ in range(len(EVE_CARDS))]
check("前夜卡 4 张抽 4 次无重复", len(set(drawn_eve)) == len(EVE_CARDS))
check("抽完后自动重洗（第 5 次仍有卡）", isinstance(scene_text(date(2026, 9, 24), 20), str))

print("── 月亮 ──")
check("前夜：差不多圆了", "差不多圆" in moon_text(date(2026, 9, 24)))
check("正日：满月文案", "满月" in moon_text(date(2026, 9, 25)))
check("十六：追月", "追月" in moon_text(date(2026, 9, 26)))
check("十七：开始亏了", "亏" in moon_text(date(2026, 9, 27)))
quiet_moon = moon_text(date(2026, 6, 10), "广州")
check("普通日：月龄+照亮+城市", "天大" in quiet_moon and "照亮" in quiet_moon and "广州" in quiet_moon, quiet_moon[:30])
check("普通日默认城市佛山", "佛山" in moon_text(date(2026, 6, 10)))

print("── 明年也在表里（2027 中秋 9/15）──")
next_year = scene_text(date(2027, 9, 15), 20)
check("2027 正日晚出天台卡", next_year in DAY_CARDS, next_year[:20])

print()
total = PASS + FAIL
print(f"{PASS}/{total} 全过" if FAIL == 0 else f"⚠ {FAIL} 个没过，共 {total}")
sys.exit(1 if FAIL else 0)
