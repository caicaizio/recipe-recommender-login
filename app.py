import os
import pandas as pd
import numpy as np
import random
from flask import request, Flask, render_template, session, jsonify
from model import recommenders, utils

import accounts                     # 新增：昵称 + 口令的账号（数据存 data/accounts.json）
import regions                      # 新增：省份 -> 主食 / 口味
import region_picks                 # 新增：按省份口味从菜谱库里挑菜

app = Flask(__name__)
# Flask 的 session 需要密钥；没设 SECRET_KEY 就随机生成一个（重启后登录态失效）
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)


@app.context_processor
def inject_regions():
    """省份表和口味表要下发到模板：登录框的选项和即时提示都用它"""
    return {"provinces": regions.PROVINCES, "regions": regions.REGIONS}


# ---------------- 新增：账号接口（右下角登录按钮用） ----------------
def current_user():
    name = session.get("user")
    return name if name and accounts.exists(name) else ""


def current_province():
    """当前登录账号选的省份；没登录或没选就是 "" """
    name = current_user()
    return accounts.province(name) if name else ""


def current_region():
    """当前账号选的省份 + 匹配到的主食口味；没登录或没选就是 None"""
    province = current_province()
    taste = regions.taste_of(province)
    if not taste:
        return None
    return {"province": province, "staple": taste["staple"], "taste": taste["taste"]}


@app.route("/api/region-picks")
def api_region_picks():
    """选了省份之后：返回符合这个口味的几道菜（登录框即时显示、首页也用）"""
    province = (request.args.get("province") or "").strip()
    try:
        n = max(1, min(12, int(request.args.get("n", 6))))
    except ValueError:
        n = 6
    return jsonify({"province": province,
                    "recipes": region_picks.picks_for(province, n)})


@app.route("/api/me")
def api_me():
    name = current_user()
    return jsonify({"name": name, "picks": len(accounts.picks(name)) if name else 0})


@app.route("/api/accounts")
def api_accounts():
    """给登录框用：列出已有账号，点一下就填昵称（顺带把各自的省份带回去）"""
    users = accounts.all_users()
    return jsonify({
        "names": list(users.keys()),
        "provinces": {n: (u.get("province") or "") for n, u in users.items()},
    })


@app.route("/api/register", methods=["POST"])
def api_register():
    body = request.get_json(force=True) or {}
    ok, msg = accounts.create(body.get("name", ""), body.get("password", ""),
                              body.get("province", ""))
    if not ok:
        return jsonify({"ok": False, "error": msg}), 400
    session["user"] = msg
    return jsonify({"ok": True, "name": msg})


@app.route("/api/login", methods=["POST"])
def api_login():
    body = request.get_json(force=True) or {}
    ok, msg = accounts.verify(body.get("name", ""), body.get("password", ""))
    if not ok:
        return jsonify({"ok": False, "error": msg}), 400
    province = (body.get("province") or "").strip()
    if province:                      # 没传就不动，避免登录时把以前选的省份清掉
        accounts.set_province(msg, province)
    session["user"] = msg
    return jsonify({"ok": True, "name": msg, "picks": len(accounts.picks(msg))})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("user", None)
    return jsonify({"ok": True})


@app.route("/api/forget", methods=["POST"])
def api_forget():
    """清空这个账号记住的菜（账号面板里的「清空」按钮）"""
    name = current_user()
    if name:
        accounts.clear_picks(name)
    return jsonify({"ok": True})


@app.route('/', methods=['GET','POST'])
def quiz():
    user = current_user()                       # 新增：当前登录的昵称（没登录是 ""）
    # choose sample to show for quiz
    most_popular = recommenders.sample_popular()

    if request.method == 'POST':
        quiz_results = request.form.getlist("my_checkbox")

        sample = random.sample(quiz_results,2) # for two categories
        title = sample[0]

        print(f'quiz results: {quiz_results}')
        print(f'title: {title}')

        ### People with Similar Tastes Also Liked ###
        user_recommended = recommenders.quiz_user_user_recommender(utils.create_new_user(quiz_results))
        print(f'user_recommended: {user_recommended}')

        ### Because you liked X ###
        item_recommended = recommenders.item_item_recommender(title=title, new_user=utils.create_new_user(quiz_results))
        # from quiz results, get category, and randomly select 2 to return recipes in that category
        print(f'item_recommended: {item_recommended}')
        ### categories ###
        cat1 = utils.get_category(sample[0])
        cat1_recommended = [utils.recipe_id_to_title(recipe) for recipe in utils.similar_to_cat(cat1)]

        cat2 = utils.get_category(sample[1])
        cat2_recommended = [utils.recipe_id_to_title(recipe) for recipe in utils.similar_to_cat(cat2)]

        cats_recommended = list([cat1_recommended,cat2_recommended])
        print(f'cats_recommended: {cats_recommended}')

        ### tastebreaker ###
        tastebreaker = recommenders.item_item_recommender(title=title, new_user=utils.create_new_user(quiz_results), opposite=True)
        print(f'tastebreaker: {tastebreaker}')

        # svd_recommended = recommenders.svd_recommender(8888888, new_user=utils.create_new_user(quiz_results))
        # print(f'svd_recommended: {svd_recommended}')
        all = user_recommended + item_recommended
        # + svd_recommended

        all = set(all) # remove duplicates
        # remove recipes user has tried & sample 6
        hybrid_recommended = random.sample([x for x in all if x not in utils.known_positives(8888888,new_user=utils.create_new_user(quiz_results))],6)

        print(f'hybrid_recommended: {hybrid_recommended}')

        return render_template("result.html",
        title = title,
        user = user,
        region = current_region(),
        regional = region_picks.picks_for(current_province(), 6),

        cats = (list([cat1,cat2]), cats_recommended, [utils.get_url(utils.title_to_id(recipe)) for recipe in cats_recommended[0]], [utils.get_url(utils.title_to_id(recipe)) for recipe in cats_recommended[1]]),
        # tuple, second element is the image url
        most_popular=([utils.strip_filler(recipe) for recipe in most_popular],
        [utils.get_url(utils.title_to_id(recipe)) for recipe in most_popular]),

        quiz_results=([utils.strip_filler(recipe) for recipe in quiz_results],
        [utils.get_url(utils.title_to_id(recipe)) for recipe in quiz_results]),

        user_recommended=([utils.strip_filler(recipe) for recipe in user_recommended],
        [utils.get_url(utils.title_to_id(recipe)) for recipe in user_recommended]),

        item_recommended=([utils.strip_filler(recipe) for recipe in item_recommended],
        [utils.get_url(utils.title_to_id(recipe)) for recipe in item_recommended],utils.strip_filler(title))
        ,

        tastebreaker=([utils.strip_filler(recipe) for recipe in tastebreaker],
        [utils.get_url(utils.title_to_id(recipe)) for recipe in tastebreaker],utils.strip_filler(title)),

        hybrid_recommended = ([utils.strip_filler(recipe) for recipe in hybrid_recommended],
        [utils.get_url(utils.title_to_id(recipe)) for recipe in hybrid_recommended])
        )

    # landing screen
    return render_template("quiz.html",
    most_popular=(most_popular,[utils.get_url(utils.title_to_id(recipe)) for recipe in most_popular]),
    user=user,
    region=current_region(),
    regional=region_picks.picks_for(current_province(), 6)
    )

if __name__ == '__main__':
    app.run(debug=True)
