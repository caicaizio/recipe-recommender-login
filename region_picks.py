"""按省份口味从菜谱库里挑菜。

做法很朴素：把这个省的每个口味标签分别翻译成英文关键词，去「菜名 + 配料表」里数命中次数。
**要求每个标签都至少命中一次**（比如广东是「清淡 + 海鲜」，那菜得既有 steamed/poached
这类词、又有 shrimp/fish 这类词），这样比「命中任意一个就算」准得多。
都满足的菜按总命中数 + 评分排序，取前 POOL 名后随机抽几道。

这终究是**关键词匹配，不是模型推荐**——可能在口味上很准，也可能只是撞了词
（比如配料里有 lemon 就算「酸口」）。页面上写明了这一点，别让人误以为是智能推荐。
"""

import regions
from model import all_recipes, utils

POOL = 40   # 只在前 40 名候选里随机取，保证每次进来看到的菜略有不同


def picks_for(province, n=6):
    """省份 -> [{"title":…, "url":…}, …]。没选省份或表里没有就返回空列表"""
    taste = regions.taste_of(province)
    if not taste:
        return []

    groups = [regions.TAG_KEYWORDS.get(t, []) for t in taste.get("tags", [])]
    groups = [g for g in groups if g]
    if not groups:
        return []

    text = (all_recipes["title"].fillna("") + " " + all_recipes["ingredients"].fillna("")).str.lower()

    # 每个标签各算一次命中数
    per_tag = [text.apply(lambda s, g=g: sum(1 for k in g if k in s)) for g in groups]
    total = sum(per_tag)

    every = per_tag[0] > 0
    for p in per_tag[1:]:
        every = every & (p > 0)

    hit = all_recipes[every].copy()
    if hit.empty:                # 两个标签都满足的太少，退一步：命中任一即可
        hit = all_recipes[total > 0].copy()
        if hit.empty:
            return []
        hit["_hits"] = total[total > 0]
    else:
        hit["_hits"] = total[every]

    hit = hit.sort_values(["_hits", "ratings"], ascending=[False, False]).head(POOL)
    chosen = hit if len(hit) <= n else hit.sample(n)
    return [{"title": utils.strip_filler(str(row["title"])),
             "url": utils.get_url(int(row["recipe_id"]))}
            for _, row in chosen.iterrows()]
