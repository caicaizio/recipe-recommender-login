/* 右上角账号：注册 / 登录 / 退出，以及「记住口令」。
   账号和口令哈希在服务端（data/accounts.json），这里只负责界面和自动填充。

   「记住口令」是浏览器这边的事：口令以混淆形式存在 localStorage，
   钥匙也在同一台机器上，所以只能挡住随手翻看，等同明文——别用它存重要密码。 */
(function () {
  "use strict";

  var PWD_KEY = "seasonings-pwd-v1";   // { 昵称: 混淆后的口令 }
  var KEY_KEY = "seasonings-key-v1";   // 本机混淆钥匙

  var knownProvinces = {};             // { 昵称: 省份 }，选已有账号时把省份一起填上
  var provinceTouched = false;         // 用户手动改过省份才回传，免得登录时把旧的清掉

  function readJSON(key, fallback) {
    try {
      var v = JSON.parse(localStorage.getItem(key) || "null");
      return v == null ? fallback : v;
    } catch (e) {
      return fallback;
    }
  }
  function writeJSON(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) {}
  }

  // ---- 混淆（不是加密）----
  function utf8Bytes(s) {
    if (typeof TextEncoder !== "undefined") return new TextEncoder().encode(s);
    var esc = unescape(encodeURIComponent(s));
    var out = new Uint8Array(esc.length);
    for (var i = 0; i < esc.length; i++) out[i] = esc.charCodeAt(i);
    return out;
  }
  function bytesToStr(b) {
    if (typeof TextDecoder !== "undefined") return new TextDecoder().decode(b);
    var s = "";
    for (var i = 0; i < b.length; i++) s += String.fromCharCode(b[i]);
    return decodeURIComponent(escape(s));
  }
  function hexToBytes(h) {
    var out = new Uint8Array(h.length / 2);
    for (var i = 0; i < out.length; i++) out[i] = parseInt(h.substr(i * 2, 2), 16);
    return out;
  }
  function bytesToHex(b) {
    var s = "";
    for (var i = 0; i < b.length; i++) s += ("0" + b[i].toString(16)).slice(-2);
    return s;
  }
  function randomHex(n) {
    var out = [];
    if (typeof crypto !== "undefined" && crypto.getRandomValues) {
      var a = new Uint8Array(n);
      crypto.getRandomValues(a);
      for (var i = 0; i < n; i++) out.push(("0" + a[i].toString(16)).slice(-2));
      return out.join("");
    }
    for (var j = 0; j < n; j++) out.push(("0" + Math.floor(Math.random() * 256).toString(16)).slice(-2));
    return out.join("");
  }
  function localKey() {
    var k = localStorage.getItem(KEY_KEY);
    if (!k || k.length < 32) {
      k = randomHex(32);
      localStorage.setItem(KEY_KEY, k);
    }
    return hexToBytes(k);
  }
  function obfuscate(str) {
    var b = utf8Bytes(str), k = localKey(), out = new Uint8Array(b.length);
    for (var i = 0; i < b.length; i++) out[i] = b[i] ^ k[i % k.length];
    return bytesToHex(out);
  }
  function deobfuscate(hex) {
    try {
      var b = hexToBytes(hex), k = localKey(), out = new Uint8Array(b.length);
      for (var i = 0; i < b.length; i++) out[i] = b[i] ^ k[i % k.length];
      return bytesToStr(out);
    } catch (e) {
      return "";
    }
  }
  function savedPwd(name) {
    var bag = readJSON(PWD_KEY, {});
    return bag[name] ? deobfuscate(bag[name]) : "";
  }
  function keepPwd(name, pwd) {
    var bag = readJSON(PWD_KEY, {});
    bag[name] = obfuscate(pwd);
    writeJSON(PWD_KEY, bag);
  }
  function forgetPwd(name) {
    var bag = readJSON(PWD_KEY, {});
    if (bag[name]) { delete bag[name]; writeJSON(PWD_KEY, bag); }
  }

  // ---- 接口 ----
  function api(path, body) {
    var opt = { headers: { "Content-Type": "application/json" }, credentials: "same-origin" };
    if (body) { opt.method = "POST"; opt.body = JSON.stringify(body); }
    return fetch(path, opt).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (d) {
        if (!r.ok) throw new Error(d.error || ("HTTP " + r.status));
        return d;
      });
    });
  }

  // ---- 界面 ----
  var el = function (id) { return document.getElementById(id); };

  function openLogin() {
    el("login-mask").classList.remove("hidden");
    el("login-msg").textContent = "";
    el("login-fill").textContent = "";
    el("login-pwd").value = "";
    el("login-remember").checked = false;
    loadAccounts(function () { autofill(); });
    showTaste();
    el("login-name").focus();
  }

  // ---- 新增：选省份 -> 立刻显示当地主食和口味 ----
  function regionTable() {
    try {
      return JSON.parse((el("region-data") || {}).textContent || "{}") || {};
    } catch (e) {
      return {};
    }
  }
  function showTaste() {
    var sel = el("login-province"), box = el("province-taste");
    if (!sel || !box) return;
    var p = sel.value, r = regionTable()[p];
    box.innerHTML = "";
    if (!p || !r) { box.classList.add("hidden"); return; }
    box.appendChild(make("div", "taste-line", "📍 " + p));
    box.appendChild(make("div", "taste-line", "主食：" + r.staple));
    box.appendChild(make("div", "taste-line", "口味：" + r.taste));
    box.classList.remove("hidden");
    loadRegionPicks(p);
  }

  // 选完省份再去后端要几道符合这个口味的菜（关键词匹配，不是模型推荐）
  function loadRegionPicks(province) {
    var box = el("province-picks");
    if (!box) return;
    box.innerHTML = "";
    box.classList.add("hidden");
    api("/api/region-picks?province=" + encodeURIComponent(province) + "&n=3")
      .then(function (d) {
        var list = d.recipes || [];
        if (!list.length) return;
        box.appendChild(make("div", "picks-title", "合这个口味的菜："));
        var row = make("div", "picks-row");
        list.forEach(function (r) {
          var card = make("div", "pick");
          var img = make("img");
          img.src = r.url;
          img.alt = r.title;
          card.appendChild(img);
          card.appendChild(make("p", null, r.title));
          row.appendChild(card);
        });
        box.appendChild(row);
        box.appendChild(make("div", "picks-note",
          "按口味关键词匹配，菜谱库是英文西餐，仅供参考"));
        box.classList.remove("hidden");
      })
      .catch(function () { /* 拉不到就算了，口味提示已经显示了 */ });
  }
  function closeLogin() { el("login-mask").classList.add("hidden"); }

  function loadAccounts(done) {
    api("/api/accounts").then(function (d) {
      var box = el("acct-quick");
      box.innerHTML = "";
      knownProvinces = d.provinces || {};
      if (!d.names || !d.names.length) { if (done) done(); return; }
      box.appendChild(make("div", "quick-label", "选一个账号（" + d.names.length + " 个）："));
      d.names.forEach(function (n) {
        var kept = !!savedPwd(n);
        var b = make("button", "chip", n + (kept ? " 🔑" : ""));
        b.type = "button";
        b.title = kept ? "已记住口令，点一下自动填充" : "没记住口令，需要手输";
        b.addEventListener("click", function () {
          el("login-name").value = n;
          el("login-msg").textContent = "";
          el("login-province").value = knownProvinces[n] || "";   // 顺带填上这个账号的省份
          showTaste();
          autofill();
          if (!savedPwd(n)) el("login-pwd").focus();
        });
        box.appendChild(b);
      });
      if (done) done();
    }).catch(function () { if (done) done(); });
  }

  function make(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  // 填了昵称就把记住的口令补上
  function autofill() {
    var name = el("login-name").value.trim();
    var saved = name ? savedPwd(name) : "";
    if (saved) {
      el("login-pwd").value = saved;
      el("login-remember").checked = true;
      el("login-fill").textContent = "已自动填上「" + name + "」记住的口令";
    } else {
      el("login-fill").textContent = "";
    }
  }

  function submit() {
    var name = el("login-name").value.trim();
    var pwd = el("login-pwd").value;
    var msg = el("login-msg");
    msg.textContent = "";
    if (!name) { msg.textContent = "先填昵称"; return; }
    var remember = el("login-remember").checked;
    var prov = el("login-province").value;
    var btn = el("login-go");
    btn.disabled = true;
    btn.textContent = "处理中…";
    // 昵称不存在就注册，存在就登录
    api("/api/accounts").then(function (d) {
      knownProvinces = d.provinces || {};
      var exists = (d.names || []).indexOf(name) >= 0;
      var payload = { name: name, password: pwd };
      if (prov || provinceTouched) payload.province = prov;
      var job = exists ? api("/api/login", payload)
                       : api("/api/register", payload);
      return job.then(function (r) {
        if (remember) keepPwd(name, pwd); else forgetPwd(name);
        location.reload();   // 服务端渲染，刷一下才是登录后的界面
      });
    }).catch(function (e) {
      btn.disabled = false;
      btn.textContent = "登录 / 注册";
      msg.textContent = e.message;
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var btn = el("acct-btn");
    if (!btn) return;

    btn.addEventListener("click", function () {
      if (btn.dataset.logged === "1") el("acct-menu").classList.toggle("hidden");
      else openLogin();
    });
    document.addEventListener("click", function (e) {
      var menu = el("acct-menu");
      if (menu && !menu.classList.contains("hidden") && e.target !== btn) menu.classList.add("hidden");
    });

    var sw = el("acct-switch");
    if (sw) sw.addEventListener("click", function () { el("acct-menu").classList.add("hidden"); openLogin(); });
    var out = el("acct-logout");
    if (out) out.addEventListener("click", function () {
      api("/api/logout", {}).then(function () { location.reload(); });
    });
    var fg = el("acct-forget");
    if (fg) fg.addEventListener("click", function () {
      if (!confirm("清空这个账号记住的菜？之后推荐会重新开始积累。")) return;
      api("/api/forget", {}).then(function () { location.reload(); });
    });

    el("login-go").addEventListener("click", submit);
    el("login-close").addEventListener("click", closeLogin);
    el("login-cancel").addEventListener("click", closeLogin);
    el("login-mask").addEventListener("click", function (e) {
      if (e.target === el("login-mask")) closeLogin();
    });
    el("login-name").addEventListener("input", function () {
      el("login-msg").textContent = "";
      autofill();
    });
    el("login-province").addEventListener("change", function () {
      provinceTouched = true;
      showTaste();
    });
    ["login-pwd"].forEach(function (id) {
      el(id).addEventListener("keydown", function (e) { if (e.key === "Enter") submit(); });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeLogin();
    });
  });
})();
