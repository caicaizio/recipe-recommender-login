"""各省 / 直辖市 / 特别行政区的「主食 + 口味」对照表，以及按口味找菜用的标签。

登录框里选了省份之后：
  1. 前端立刻用 staple / taste 把该地区的主食和口味显示出来；
  2. 后端用 tags 去菜谱库里挑出符合这个口味的菜（见 region_picks.py）。

这份数据是前后端共用的唯一来源。只是饮食口味的大致归纳，同一省内差异也很大，
而且菜谱库是英文的 allrecipes、匹配靠关键词，不能当标准答案看。
"""

# staple = 当地常吃的主食，taste = 口味倾向，tags = 用来找菜的口味标签
REGIONS = {
    "北京": {"staple": "面食（炸酱面、馒头、烙饼）", "taste": "咸香酱浓，芝麻酱和黄酱打底，口味厚重",
             "tags": ["烤香", "咸鲜"]},
    "天津": {"staple": "面食（煎饼馃子、包子、捞面）", "taste": "咸鲜微甜，酱香突出，爱葱蒜",
             "tags": ["咸鲜", "海鲜"]},
    "河北": {"staple": "面食（馒头、面条、烙饼）", "taste": "咸鲜为主，朴实偏重，少甜",
             "tags": ["咸鲜", "烤香"]},
    "山西": {"staple": "面食（刀削面、猫耳朵、莜面）", "taste": "酸香突出，无醋不欢，咸鲜少甜",
             "tags": ["酸", "咸鲜"]},
    "内蒙古": {"staple": "面食 + 牛羊肉（焙子、手把肉、奶茶）", "taste": "咸香浓郁，奶香与烧烤味重",
               "tags": ["烤香", "奶香"]},
    "辽宁": {"staple": "大米 + 面食", "taste": "咸鲜偏重，爱炖菜和酱，也吃酸甜口（锅包肉）",
             "tags": ["海鲜", "鲜甜"]},
    "吉林": {"staple": "大米（东北大米）+ 玉米", "taste": "咸鲜为主，喜炖煮，冬季口味重",
             "tags": ["烤香", "咸鲜"]},
    "黑龙江": {"staple": "大米 + 面食", "taste": "咸鲜偏重，酱炖为主，酸菜与熏酱风味突出",
               "tags": ["酸", "咸鲜"]},
    "上海": {"staple": "大米（米饭、泡饭、年糕）", "taste": "浓油赤酱偏甜，讲究本味的鲜",
             "tags": ["鲜甜", "咸鲜"]},
    "江苏": {"staple": "大米（米饭、河鲜）", "taste": "清淡鲜甜，淮扬偏甜，徐州一带偏咸辣",
             "tags": ["清淡", "海鲜"]},
    "浙江": {"staple": "大米（米饭、年糕、米线）", "taste": "清淡鲜嫩，微甜少油，重原味与腌鲜",
             "tags": ["清淡", "海鲜"]},
    "安徽": {"staple": "大米 + 面食", "taste": "咸鲜微辣，重油重色，火腿与臭鳜鱼是标志",
             "tags": ["咸鲜", "烤香"]},
    "福建": {"staple": "大米（米饭、米粉、地瓜）", "taste": "清淡鲜甜，海鲜与红糟入菜，汤水多",
             "tags": ["清淡", "海鲜"]},
    "江西": {"staple": "大米（米粉、瓦罐汤）", "taste": "鲜辣为主，辣得直白，爱辣椒炒肉与粉蒸",
             "tags": ["辣", "咸鲜"]},
    "山东": {"staple": "面食（馒头、煎饼、水饺）", "taste": "咸鲜为主，葱香酱香重，整体偏咸",
             "tags": ["咸鲜", "海鲜"]},
    "河南": {"staple": "面食（烩面、馒头、胡辣汤）", "taste": "咸鲜居中，胡辣微麻，爱汤水",
             "tags": ["辣", "咸鲜"]},
    "湖北": {"staple": "大米（热干面、米饭、藕汤）", "taste": "咸鲜微辣，重「鲜」，早点文化浓",
             "tags": ["清淡", "咸鲜"]},
    "湖南": {"staple": "大米（米粉、米饭）", "taste": "鲜辣重辣，剁椒与腊味突出，麻味少",
             "tags": ["辣", "咸鲜"]},
    "广东": {"staple": "大米（米饭、河粉、肠粉）", "taste": "清淡鲜甜，讲镬气与原味，白切清蒸为主",
             "tags": ["清淡", "海鲜"]},
    "广西": {"staple": "大米（米粉、螺蛳粉、糯米饭）", "taste": "酸辣鲜爽，酸笋与螺蛳味独特",
             "tags": ["酸", "辣"]},
    "海南": {"staple": "大米（米饭、海南粉、椰子饭）", "taste": "清淡鲜甜，椰香与海鲜突出，少油",
             "tags": ["清淡", "海鲜"]},
    "重庆": {"staple": "大米 + 小面", "taste": "麻辣霸道，牛油与花椒当家，重油重辣",
             "tags": ["麻辣", "辣"]},
    "四川": {"staple": "大米（米饭、担担面）", "taste": "麻辣鲜香，复合味型多（鱼香、怪味），花椒突出",
             "tags": ["麻辣", "辣"]},
    "贵州": {"staple": "大米（米粉、糯米饭）", "taste": "酸辣为主，糟辣椒与酸汤独特，万物皆可蘸水",
             "tags": ["酸", "辣"]},
    "云南": {"staple": "大米（米线、饵块）", "taste": "酸辣鲜香，菌菇鲜花入菜，蘸水丰富",
             "tags": ["辣", "咸鲜"]},
    "西藏": {"staple": "青稞（糌粑、青稞面）", "taste": "咸香厚重，酥油与牦牛肉为主，口味淳朴",
             "tags": ["烤香", "奶香"]},
    "陕西": {"staple": "面食（biangbiang 面、泡馍、肉夹馍）", "taste": "酸辣咸香，油泼辣子配陈醋当家",
             "tags": ["酸", "辣"]},
    "甘肃": {"staple": "面食（兰州牛肉面、洋芋搅团）", "taste": "咸鲜香辣，牛羊肉与孜然，喜酸辣",
             "tags": ["辣", "烤香"]},
    "青海": {"staple": "面食 + 青稞（尕面片、糌粑）", "taste": "咸香为主，牛羊肉与酸奶，清真风味",
             "tags": ["烤香", "奶香"]},
    "宁夏": {"staple": "面食 + 牛羊肉（手抓羊肉、羊杂碎）", "taste": "咸香微辣，清真风味，面食扎实",
             "tags": ["烤香", "辣"]},
    "新疆": {"staple": "面食（馕、拌面、抓饭）", "taste": "咸香浓郁，孜然与羊肉为主，带番茄酸香",
             "tags": ["烤香", "酸"]},
    "台湾": {"staple": "大米（卤肉饭、面线、便当）", "taste": "清淡鲜甜，卤香与酱香突出，小吃发达",
             "tags": ["鲜甜", "海鲜"]},
    "香港": {"staple": "大米（米饭、云吞面、烧腊饭）", "taste": "清淡鲜香，粤式烧腊与茶餐厅，鲜甜少辣",
             "tags": ["清淡", "海鲜"]},
    "澳门": {"staple": "大米（粥面、猪扒包、葡国菜）", "taste": "中西合璧，咸鲜微甜，带咖喱与椰香",
             "tags": ["烤香", "鲜甜"]},
}

PROVINCES = list(REGIONS.keys())

# 口味标签 -> 在菜名和配料表里找的英文关键词（菜谱库是英文的，只能用英文匹配）
TAG_KEYWORDS = {
    "酸": ["sour", "vinegar", "vinegary", "lemon", "lime", "pickle", "tangy",
           "sauerkraut", "cider vinegar", "balsamic"],
    "辣": ["spicy", "chili", "chile", "chipotle", "cayenne", "jalapeno", "jalapeño",
           "hot sauce", "sriracha", "paprika", "pepper flakes", "curry"],
    "麻辣": ["sichuan", "szechuan", "peppercorn", "numbing", "dan dan", "mapo"],
    # 注意：别往这里塞 light / onion / broth 这种几乎每道菜都有的词，
    # 否则「每个标签都要命中」这个约束就形同虚设，广东会给你端出咖喱。
    "清淡": ["steamed", "poached", "boiled", "clear soup", "consomme",
             "garden salad", "simple"],
    "鲜甜": ["honey", "caramel", "brown sugar", "maple", "glazed", "cinnamon", "sweet"],
    "咸鲜": ["soy sauce", "garlic", "mushroom", "parmesan", "savory",
             "oyster sauce", "miso", "anchovy"],
    "奶香": ["cream", "butter", "cheese", "cheesy", "milk", "yogurt", "yoghurt"],
    "烤香": ["grill", "grilled", "barbecue", "bbq", "roasted", "roast", "cumin",
             "smoked", "baked"],
    "海鲜": ["shrimp", "prawn", "salmon", "tuna", "crab", "fish", "scallop",
             "seafood", "clam", "lobster", "cod"],
}


def taste_of(province):
    """省份 -> {"staple":…, "taste":…, "tags":[…]}；没选或表里没有就返回 None"""
    if not province:
        return None
    return REGIONS.get(province.strip())


def keywords_of(province):
    """省份 -> 这个口味对应的英文关键词列表"""
    taste = taste_of(province)
    if not taste:
        return []
    out = []
    for tag in taste.get("tags", []):
        out.extend(TAG_KEYWORDS.get(tag, []))
    return out
