# -*- coding: utf-8 -*-
"""Build index.html (interactive) + print.html (A4 PDF source) from data/*.json.
Edit data/*.json or the PLAN below, then run:  python build.py  (then render PDF)."""
import json, html, re, urllib.parse
from pypinyin import lazy_pinyin
import opencc

T2S = opencc.OpenCC("t2s")
D = "data/"
q = json.load(open(D + "quanzhou.json", encoding="utf-8"))
x = json.load(open(D + "xiamen.json", encoding="utf-8"))
L = json.load(open(D + "logistics.json", encoding="utf-8"))
IMG = json.load(open(D + "img_meta.json", encoding="utf-8"))
S = {s["id"]: s for s in q["stops"] + x["stops"]}

TITLE = "廈門・泉州 極致奢享深度遊"
PDF_NAME = "廈門泉州極致奢享_深度遊行程規劃指南.pdf"

def e(t):
    return html.escape(str(t if t is not None else ""))

def fix(t):
    t = str(t if t is not None else "")
    t = t.replace("（見notes.traffic_restrictions）", "（見「出發前必看」第 2 點）").replace("estimate", "估算")
    return t.replace("unverified", "未核實").replace("Unverified", "未核實")

# ---------------------------------------------------------------- extra stops
X = {}
def add(id, **kw):
    base = dict(id=id, type="transport", name_trad="", name_simp="", address_simp="", hours="", closed="",
                ticket="", booking="", transport_from_prev="", signboard="", street_sign="", wayfinding="",
                must_order=[], insider_tip="", metro={})
    base.update(kw); X[id] = base

add("t_flight_out", name_trad="去程班機：華信 AE991（華航 CI991 共掛）", name_simp="厦门高崎国际机场 T3",
    hours="12/24(四) 桃園 T2 08:40 → 廈門高崎 T3 10:30（2026/27 冬季班表，訂票時再確認）",
    ticket="經濟艙約 NT$11,000 起（華航官網參考價）", booking="立即訂位：12/25 為台灣行憲紀念日連假，機位緊。替代：廈航 MF888 桃園 11:10 → 12:50",
    transport_from_prev="桃園機場第二航廈（T2）報到；起飛前 2 小時抵達",
    signboard="入境大廳指標：「台湾居民」通道／「入境 Arrivals」／「行李提取」",
    street_sign="", wayfinding="落地後走「台湾居民／中国公民」通道，刷卡式台胞證入境 → 領行李 → 跟著「出租车 / 空港快线」指標出到達層。",
    insider_tip="⚠️ 12/24 很可能是高崎機場最後營運日（新翔安機場預計 12/25 啟用）。去程仍降落高崎 T3；請在 12 月中再確認航空公司通知。",
    metro={"line": "✈ 航班", "color": "#0f2a44", "station": "TPE T2 → XMN T3", "exit": ""})
add("t_to_train", name_trad="高崎機場 → 廈門北站 → 動車到泉州", name_simp="厦门北站",
    hours="建議車次：D2290 廈門北 12:26 → 泉州 12:58，或 D3290 12:31 → 13:03（後備 D3206 12:52 → 13:24）",
    ticket="二等座 ¥27–32／一等座 ¥43–50（攜程 2026/10 查詢）",
    booking="12306 App 以台胞證註冊（線上即時核驗），12/24 車票約 12/10 開賣；站名務必選「泉州」（不是泉州東／泉州南）",
    transport_from_prev="計程車 25–35 分鐘、約 ¥50–70；或空港快線「北站專線」¥15（T3 國內到達層 7 號門西側約 80 m，約每 20 分一班）",
    signboard="車站指標：「进站口」→「检票口」→ 看大螢幕「车次 D2290 / 终到 泉州」",
    wayfinding="進站：刷台胞證過實名閘機（讀不到就走「人工通道」）。廈門北到泉州班次多（約 82 班／日），比廈門站（約 22 班）方便很多。",
    insider_tip="10:30 落地 → 入境＋領行李約 45–60 分 → 計程車 30 分 → 約 12:00 抵廈門北，訂 12:26 那班留緩衝。",
    metro={"line": "動車 D", "color": "#1f6fb2", "station": "厦门北 → 泉州", "exit": ""})
add("t_qz_hotel", name_trad="泉州站 → 酒店寄放行李", name_simp="泉州滨江皇冠假日酒店",
    hours="約 13:00–13:30 抵達；入住 15:00，先寄放行李",
    transport_from_prev="泉州站出站後跟「出租车」或「网约车上车点」指標；計程車約 20–30 分鐘、¥25–40（估算）",
    signboard="泉州站出口指標：「出站口」「出租车」「网约车」", street_sign="江滨南路",
    wayfinding="酒店在晉江南岸江濱南路，不在古城內。進古城每次叫車約 10–20 分鐘。",
    insider_tip="先寄放行李、拿房卡預登記，就可以輕裝出門吃午餐。",
    metro={"line": "🚕 滴滴／計程車", "color": "#6b7280", "station": "泉州站 → 江滨南路", "exit": ""})
add("t_charter", name_trad="包車移師：泉州 → 晉江 → 廈門", name_simp="五店市传统文化旅游区",
    hours="09:30 退房上車 → 10:00 五店市 → 12:15 梧林 → 14:15 出發 → 約 15:45–16:00 抵沙坡尾",
    ticket="半日包車估計 ¥400–650（含過路費需確認；請向 Trip.com／Klook／酒店禮賓詢價）",
    booking="出發前 1–2 週預訂；確認車型可放 2 個行李箱＋含停車過路費",
    transport_from_prev="酒店門口上車，行李全程留車上",
    signboard="",
    wayfinding="不包車也可以：滴滴分三段（酒店→五店市→梧林→沙坡尾）約 ¥300–420，但要自己拖行李，五店市／梧林能否寄放行李未核實。",
    insider_tip="週六走這條「泉州 → 晉江僑鄉 → 廈門」順路單向線，完全不走回頭路。",
    metro={"line": "🚗 包車", "color": "#7c3aed", "station": "泉州 → 晉江 → 廈門島", "exit": ""})
add("t_flight_back", name_trad="回程班機：廈航 MF881 → 台北松山", name_simp="厦门翔安国际机场",
    hours="12/28(一) 廈門 17:10 → 松山 18:45（每日；機場轉場後時刻可能微調，12 月中再確認）",
    ticket="", booking="與去程一起訂「桃園去／松山回」多段票，或兩張單程。替代：立榮 B7512 12:35 → 松山 14:20（週一有班）",
    transport_from_prev="見上一站：沙坡尾 13:30 出發往翔安機場",
    signboard="出發層指標：「出发 Departures」→「国际及港澳台 值机」",
    wayfinding="兩岸航班走「国际及港澳台」區報到與出境；退稅（滿 ¥200）需在出境前辦理。",
    insider_tip="新機場啟用第 4 天，動線不熟、可能排隊：起飛前 2.5 小時到。",
    metro={"line": "✈ 航班", "color": "#0f2a44", "station": "翔安 → TSA", "exit": ""})
S.update(X)

# ---------------------------------------------------------------- day plan
# (stop_id, time label, optional note)
PLAN = [
 dict(day=1, date="12/24（四）", city="泉州", title="抵達・泉州城南：媽祖廟、古城門與平安夜小院晚餐",
      free="14:45–15:30 慢慢走過涂門街、喝杯茶；晚餐後自由回酒店",
      items=[("t_flight_out", "08:40"), ("t_to_train", "11:00"), ("hotel", "13:00 寄放行李"),
             ("f_haochengcai", "14:00 遲午餐", "13:30 後不用排隊，正好錯開飯點"),
             ("d1_tianhougong", "15:30"), ("d1_dejimen", "16:40"), ("f_bingzheng", "16:50 點心"),
             ("f_lvdoubing", "順路伴手"), ("d1_jubaojie", "17:00 黃昏"), ("f_d1_dinner_haoting", "18:30 晚餐")]),
 dict(day=2, date="12/25（五）", city="泉州", title="古城背巷：開元寺清晨、小巷東西塔、承天寺與鹽燒薑母鴨",
      free="13:00–14:45 回酒店午休／泳池，或在承天巷咖啡館歇腳",
      items=[("f_d2_breakfast_luoji", "07:30 早餐"), ("d2_kaiyuansi", "08:15"), ("d2_lanes", "10:00"),
             ("f_yafo", "順路點心"), ("f_d2_lunch_houapo", "11:45 午餐"), ("d2_free", "13:00 留白"),
             ("d2_wenmiao", "15:00"), ("d2_jinyuxiang", "15:50"), ("d2_chengtiansi", "16:30"),
             ("f_d2_dinner_zhongji", "18:00 晚餐"), ("f_d2_night_option", "宵夜選項")]),
 dict(day=3, date="12/26（六）", city="晉江 → 廈門", title="僑鄉移師日：五店市、梧林番仔樓，傍晚沙坡尾與演武大橋日落",
      free="車上休息；晚餐後沙坡尾酒吧／書店自由逛約 2 小時",
      items=[("t_charter", "09:30 退房"), ("d3_wudianshi", "10:00"), ("f_d3_lunch", "11:00 午餐"),
             ("d3_wulin", "12:15"), ("X00", "16:00 入住"), ("X01", "16:30"), ("X02", "17:00 日落"), ("X03", "18:30 晚餐")]),
 dict(day=4, date="12/27（日）", city="廈門", title="老廈門：八市早市、南洋騎樓 CityWalk、鼓浪嶼安靜西側",
      free="17:00 回酒店後整晚自由；騎樓散步途中隨意停留",
      items=[("X04", "07:30"), ("X05", "早餐"), ("X06", "早餐"), ("X07", "選吃"), ("X08", "選項"),
             ("X09", "09:00"), ("X10", "午餐"), ("X11", "選吃"), ("X12", "選吃"), ("X13", "12:40"), ("X14", "13:30"),
             ("X15", "選吃")]),
 dict(day=5, date="12/28（一）", city="廈門 → 台北", title="慢早晨：沙茶麵、南普陀、廈大校園，傍晚飛回松山",
      free="12:00–13:30 大學路咖啡、回酒店取行李",
      items=[("X16", "07:30 早餐"), ("X17", "替代早餐"), ("X18", "08:15"), ("X19", "09:30"), ("X20", "10:30"),
             ("X21", "12:00"), ("X22", "13:30 出發"), ("t_flight_back", "17:10")]),
]

PHOTOS = {
 "d1_tianhougong": [("tianhougong", "實景：泉州天后宮大殿（世界遺產點）")],
 "d1_dejimen": [("dejimen_plaque", "實景：德濟門遺址文保石碑，認明「德济门遗址」"), ("dejimen_ruins", "實景：下沉式宋元城門遺址")],
 "d1_jubaojie": [("shunjiqiao", "實景：聚寶街旁晉江上的順濟橋遺址")],
 "f_d2_breakfast_luoji": [("mianxianhu", "示意：泉州麵線糊（非羅記本店照片）")],
 "d2_kaiyuansi": [("kaiyuan_hall", "實景：開元寺大雄寶殿"), ("kaiyuan_pagoda", "實景：東塔「镇国塔」")],
 "d2_lanes": [("xijie_lane", "實景：西街背巷（台魁巷）"), ("xijie_view", "實景：西街屋頂與開元寺塔")],
 "f_d2_lunch_houapo": [("clock_tower", "實景：泉州鐘樓，侯阿婆在鐘樓東側東街")],
 "d2_wenmiao": [("wenmiao", "實景：泉州府文廟大成殿")],
 "d2_chengtiansi": [("chengtiansi_gate", "實景：承天寺山門"), ("chengtiansi_stele", "實景：「承天寺」石碑")],
 "f_d2_dinner_zhongji": [("jiangmuya", "示意：泉州薑母鴨（非忠記本店照片）")],
 "f_yafo": [("runbing", "示意：潤餅捲（非亞佛本店照片）")],
 "X00": [("shimao_towers", "實景：酒店旁地標世茂海峽大廈雙子塔（Commons 無酒店本身照片）")],
 "X01": [("shapowei_boats", "實景：沙坡尾避風塢漁船"), ("shapowei_harbour", "實景：避風塢與老漁民屋")],
 "X02": [("yanwu_sunset", "實景：演武大橋觀景平台日落")],
 "X06": [("shachamian", "示意：海鮮沙茶麵（非友生本店照片）")],
 "X07": [("tusundong", "示意：廈門土筍凍")],
 "X09": [("datong_road", "實景：廈門大同路騎樓街"), ("arcade_houses", "實景：大同路老騎樓立面")],
 "X11": [("oyster_omelette", "示意：海蠣煎（非蓮歡本店照片）")],
 "X12": [("huangzehe", "實景：黃則和花生湯店門面，認明「黄则和花生汤」紅底金字招牌")],
 "X13": [("gulangyu_ferry", "實景：廈鼓航線渡輪與鼓浪嶼")],
 "X14": [("zhongdegong", "實景：鼓浪嶼內厝澳種德宮")],
 "X16": [("shacha_shop", "示意：廈門沙茶麵老店門面（四里沙茶麵，非烏糖）")],
 "X18": [("nanputuo", "實景：南普陀寺")],
 "X20": [("xmu_jiannan", "實景：廈大建南大會堂"), ("xmu_furong", "實景：芙蓉湖與嘉庚樓群")],
}

ENTRANCE = {
 "d1_tianhougong": "中山南路 08:00–23:00 禁行機動車 → 滴滴目的地填「德济门遗址」或「天后路」，下車即見紅磚山門",
 "d2_kaiyuansi": "西街東段 08:00–23:00 禁行機動車 → 滴滴填「开元寺西门」公交站一帶；正門在西街 176 號、紫雲屏照壁正對面",
 "d2_lanes": "開元寺正門對面「紫云屏」照壁後方即象峰巷入口",
 "d2_wenmiao": "滴滴目的地填「泉州府文庙」涂门街側（涂门街不在禁行段）",
 "f_haochengcai": "滴滴填「通淮关岳庙」，招牌在關岳廟正對面一側",
 "f_d2_dinner_zhongji": "25 路公車「东门」站步行約 5 分鐘；滴滴填「忠记盐烧番鸭」",
 "d2_chengtiansi": "西門入：公交 10／25／K1／X1「承天寺」站步行 50 m",
 "X04": "地鐵 1 號線「镇海路」站 3 號口（遊記資料，未核實），或計程車到「开禾路口」",
 "X13": "東渡郵輪中心：跟著「厦鼓码头 / 鼓浪屿」指標，刷台胞證／二維碼過閘",
 "X14": "在「内厝澳码头」下船（不是三丘田／鋼琴碼頭），上岸往康泰路",
 "X18": "東山門進、西山門出；入寺要出示預約碼＋台胞證原件",
 "X20": "只能從「厦门大学访客中心」（新南門，演武路地下停車場旁）入校；台胞證走人工核驗工作台",
 "X02": "從「世茂海峡大厦」旁入口下到平台最近",
 "X22": "車到「出发」層，找「国际及港澳台」值機區",
}

AMAPQ = {
 "d1_jubaojie": "泉州聚宝街", "d2_lanes": "泉州象峰巷", "d2_jinyuxiang": "泉州金鱼巷", "X09": "厦门大同路",
 "X13": "厦门国际邮轮中心厦鼓码头", "X14": "鼓浪屿种德宫", "X21": "厦门大学路邮局咖啡", "X22": "厦门翔安国际机场",
 "X01": "沙坡尾艺术西区", "X04": "厦门第八市场", "t_flight_out": "厦门高崎国际机场T3", "t_to_train": "厦门北站",
 "t_qz_hotel": "泉州滨江皇冠假日酒店", "t_charter": "五店市传统文化旅游区", "t_flight_back": "厦门翔安国际机场",
 "hotel": "泉州滨江皇冠假日酒店", "X00": "厦门大学沙坡尾海景亚朵见野酒店",
}

def amap(stop):
    if stop["id"] == "d2_free":
        return ""
    qv = AMAPQ.get(stop["id"])
    if not qv:
        qv = re.split(r"[／/→]", stop.get("name_simp") or "")[0].strip()
        city = "泉州" if stop["id"].startswith(("d", "f_", "hotel")) else "厦门"
        if stop["id"].startswith(("d3", "f_d3")):
            city = "晋江"
        if not qv.startswith(("泉州", "厦门", "晋江", "鼓浪屿")):
            qv = city + " " + qv
    qv = T2S.convert(qv)
    return "https://www.amap.com/search?query=" + urllib.parse.quote(qv)

def pinyin(t):
    return " ".join(w.upper() for w in lazy_pinyin(T2S.convert(t)) if w.strip())

def street_signs(t):
    t = fix(t)
    parts = [p.strip() for p in re.split(r"[／/、]", t) if p.strip() and p.strip() not in ("—", "-")]
    out = []
    for p in parts[:5]:
        p2 = re.sub(r"[（(].*?[)）]", "", p).strip()
        if not p2 or len(p2) > 10:
            continue
        sp = T2S.convert(p2)
        out.append(f'<span class="roadsign"><b>{e(sp)}</b><i>{e(pinyin(sp))}</i></span>')
    return "".join(out)

def pill(m):
    if not m or not m.get("line") or m.get("line") in ("—",):
        return '<span class="pill" style="background:#6b7280">🚕 滴滴／計程車／步行</span>'
    col = m.get("color") or "#6b7280"
    st = m.get("station") or ""
    ex = m.get("exit") or ""
    s = f'<span class="pill" style="background:{e(col)}">{e(m["line"])}</span>'
    if st and st != "—":
        s += f' <code class="stcode">{e(st)}</code>'
    if ex and ex != "—":
        s += f' <span class="muted">{e(fix(ex))}</span>'
    return s

TYPE = {"sight": ("景點", "#0f2a44"), "food": ("美食", "#b5532f"), "hotel": ("住宿", "#8a6d1f"), "transport": ("交通", "#1f6fb2")}

def card(stop, time, note=""):
    st = stop
    tlabel, tcol = TYPE.get(st["type"], ("", "#333"))
    imgs = PHOTOS.get(st["id"], [])
    ph = ""
    if imgs:
        figs = "".join(
            f'<figure class="ph"><div class="ratio"><img loading="lazy" src="{e(IMG[k]["src"])}" alt="{e(c)}" onerror="this.closest(\'figure\').style.display=\'none\'"></div>'
            f'<figcaption>{e(c)} · <a href="{e(IMG[k]["commons"])}">Wikimedia Commons</a></figcaption></figure>'
            for k, c in imgs)
        ph = f'<div class="phs n{len(imgs)}">{figs}</div>'
    elif st["type"] in ("sight", "hotel"):
        ph = '<p class="nophoto">📷 Wikimedia Commons 無可靠授權實景照：抵達前請在高德地圖點開地點看「实景」照片核對門面。</p>'
    mo = ""
    if st.get("must_order"):
        rows = "".join(f'<tr><td class="simp">{e(fix(m.get("simp")))}</td><td>{e(fix(m.get("trad")))}</td><td>{e(fix(m.get("price")))}</td></tr>' for m in st["must_order"])
        mo = f'<table class="order"><thead><tr><th>菜單原文（指給店員看）</th><th>繁體</th><th>參考價</th></tr></thead><tbody>{rows}</tbody></table>'
    ent = ENTRANCE.get(st["id"]) or (f'滴滴／高德目的地輸入：「{T2S.convert(re.split(r"[／/→]", st.get("name_simp") or "")[0].strip())}」' if st.get("name_simp") and st["name_simp"] != "—" else "")
    info = []
    for lab, k in (("營業時間", "hours"), ("休息日", "closed"), ("門票／價位", "ticket"), ("預約", "booking"), ("地址", "address_simp")):
        v = st.get(k)
        if v and v not in ("—", "無", "-"):
            extra = ""
            if k == "hours" and st.get("hours_source_url"):
                extra = f' <a class="src" href="{e(st["hours_source_url"])}">來源</a>'
            info.append(f'<div><dt>{lab}</dt><dd>{e(fix(v))}{extra}</dd></div>')
    am = amap(st)
    amb = f'<a class="btn amap" href="{am}" target="_blank" rel="noopener">📍 高德地圖導航</a>' if am else ""
    sign_simp = re.split(r"[／/→]", st.get("name_simp") or "")[0].strip()
    signboard = ""
    if sign_simp and sign_simp != "—":
        signboard = f'<div class="signboard">{e(T2S.convert(sign_simp))}</div>'
    rs = street_signs(st.get("street_sign", ""))
    five = f"""
    <div class="five">
      <div class="el"><span class="ic">🚇</span><div><h5>交通方式與路線</h5><p>{pill(st.get("metro"))}</p><p>{e(fix(st.get("transport_from_prev")))}</p></div></div>
      <div class="el"><span class="ic">🚪</span><div><h5>下車點／入口指示關鍵字</h5><p>{e(fix(ent))}</p></div></div>
      <div class="el"><span class="ic">🪧</span><div><h5>現場路牌核對（大陸藍底白字＋拼音）</h5><p>{rs or '<span class="muted">—</span>'}</p></div></div>
      <div class="el"><span class="ic">🏷️</span><div><h5>現場招牌原文（簡體）</h5>{signboard}<p>{e(fix(st.get("signboard")))}</p></div></div>
      <div class="el wide"><span class="ic">🚶</span><div><h5>步行動線與辨識提示</h5><p>{e(fix(st.get("wayfinding")))}</p></div></div>
    </div>"""
    if st["id"] == "d2_free":
        five = ""
    tip = f'<p class="tip">💡 {e(fix(st.get("insider_tip")))}</p>' if st.get("insider_tip") else ""
    nt = f'<p class="note">⏱ {e(note)}</p>' if note else ""
    return f"""
  <article class="card no-break" id="{e(st['id'])}">
    <header class="ch"><span class="time">{e(time)}</span><span class="badge" style="background:{tcol}">{tlabel}</span>
      <h4>{e(fix(st['name_trad']))}</h4>{amb}</header>
    {nt}{ph}
    <dl class="info">{''.join(info)}</dl>
    {mo}{five}{tip}
  </article>"""

# ---------------------------------------------------------------- sections
def day_section(p):
    cards = "".join(card(S[i[0]], i[1], i[2] if len(i) > 2 else "") for i in p["items"])
    return f"""
<section class="day page-break" data-day="{p['day']}" id="day{p['day']}">
  <div class="dayhead"><div class="dnum">DAY {p['day']}</div><div><p class="ddate">{e(p['date'])} · {e(p['city'])}</p><h3>{e(p['title'])}</h3>
  <p class="free">🌿 留白時間：{e(p['free'])}</p></div></div>
  {cards}
</section>"""

def overview():
    rows = "".join(f"<tr><td><b>D{p['day']}</b> {e(p['date'])}</td><td>{e(p['city'])}</td><td>{e(p['title'])}</td></tr>" for p in PLAN)
    return f"""
<section id="overview" class="sec" data-day="0">
  <h2>行程總覽 <small>Itinerary at a Glance</small></h2>
  <div class="grid2">
   <div class="box"><h4>✈ 航班（訂票時再確認）</h4>
    <p><b>去程</b> 12/24（四）華信 AE991／華航 CI991　桃園 T2 08:40 → 廈門高崎 T3 10:30</p>
    <p><b>回程</b> 12/28（一）廈航 MF881　廈門（預計翔安新機場）17:10 → 台北松山 18:45</p>
    <p class="muted">週四松山沒有上午班機，所以去程走桃園、回程回松山；可訂多段票或兩張單程。</p></div>
   <div class="box"><h4>🏨 住宿</h4>
    <p><b>12/24–12/25（2 晚）</b> 泉州濱江皇冠假日酒店 Crowne Plaza Quanzhou Riverview<br><span class="simp">泉州市鲤城区江滨南路2233号</span>｜入住 15:00／退房 12:00｜+86 595-3601-8888</p>
    <p><b>12/26–12/27（2 晚）</b> 廈門大學沙坡尾海景亞朵見野酒店<br><span class="simp">厦门市思明区沙坡尾58号</span>｜2026 新開幕、面避風塢｜0592-5555899</p></div>
  </div>
  <table class="zebra"><thead><tr><th>日期</th><th>城市</th><th>主題</th></tr></thead><tbody>{rows}</tbody></table>
  <p class="muted">動線設計：先泉州（12/24–25 為大陸平日，古城人最少）→ 12/26 週六包車經晉江僑鄉南下 → 廈門過週末 → 12/28 從廈門直接回台，全程單向不折返。旅伴：2 位成人（情侶），節奏以悠閒為主，每日留白 1–2 小時以上。</p>
</section>"""

def alerts():
    return """
<section id="alerts" class="sec" data-day="0">
  <h2>⚠️ 出發前必看 <small>Critical Alerts</small></h2>
  <ol class="alerts">
   <li><b>廈門機場搬家：</b>官方公告翔安國際機場「2026 年底」啟用、高崎同步關閉；民航華東局計畫與維基百科寫 12/24 夜間轉場、12/25 起啟用（截至 2026/10/25 仍為「預計」）。→ 去程 12/24 應仍降落高崎 T3；<b>回程 12/28 幾乎確定從翔安機場出發</b>，沙坡尾搭車約 55–70 分鐘、¥120–160（估算）。12 月中請再確認航空公司通知。</li>
   <li><b>泉州古城交通管制（2026/10/08–2027/04/07）：</b>西街東段、中山中路／中山南路多段 08:00–23:00 禁行機動車。叫車目的地請填禁行區外：「开元寺西门」「涂门街」「德济门遗址／天后路」。古城內可搭「小白」電瓶觀光車 ¥2／人（6:30–22:00）。</li>
   <li><b>廈門大學採「預約＋搖號」：</b>12/25 00:00 開放登記 12/28 時段，不保證抽中；台胞證須到新南門訪客中心人工核驗。沒抽中就改走演武路、白城沙灘外圍。</li>
   <li><b>鼓浪嶼船票只能線上實名買：</b>「屿见厦门」小程序，提前 10–15 天放票（來源說法不一），請 12/12 起每天查。小程序可能需要大陸手機號（未核實）。訂不到的備案：華新路華僑新村老別墅散步。</li>
   <li><b>南普陀寺需預約：</b>「南普陀寺预约服务平台」小程序，最多提前 4 天（12/24 起可約 12/28），入寺要出示台胞證原件。</li>
   <li><b>台灣 12/25（五）行憲紀念日連假：</b>機位與兩岸航班需求高，請盡早訂票。</li>
   <li><b>資料可信度：</b>本手冊於 2026/10/25 聯網查核。標示「未核實」者為單一來源或推估，出發前一週請用大眾點評／高德地圖再確認營業狀態。</li>
  </ol>
</section>"""

METRO_ROWS = x.get("metro_lines", [])
def transit():
    mrows = "".join(
        f'<tr><td><span class="pill" style="background:{e(m["color_hex"])}">{e(m["line"])}</span></td><td>{e(m["color_name"])} <code>{e(m["color_hex"])}</code></td>'
        f'<td class="simp">{e(m["termini"])}</td><td>{e(m["status"])}</td><td>{e(m["key_stations_for_trip"])}</td></tr>' for m in METRO_ROWS)
    signs = [("出口", "出口", "Exit"), ("出租车", "計程車", "Taxi"), ("网约车上车点", "網約車（滴滴）上車點", "Ride-hailing pick-up"),
             ("进站口", "進站口", "Entrance"), ("检票口", "剪票口", "Ticket gate"), ("出站口", "出站口", "Exit (station)"),
             ("到达", "入境／抵達", "Arrivals"), ("出发", "出發", "Departures"), ("台湾居民", "台灣居民通道", "Taiwan residents"),
             ("行李提取", "領取行李", "Baggage claim"), ("人工通道", "人工驗證通道", "Staffed lane"), ("厦鼓码头", "廈門往鼓浪嶼碼頭", "Xiamen–Gulangyu pier"),
             ("卫生间", "洗手間", "Toilet"), ("寄存处", "行李寄放處", "Left luggage"), ("禁止通行", "禁止通行", "No entry")]
    srows = "".join(f'<tr><td class="signcell"><span class="signboard sm">{e(a)}</span></td><td>{e(b)}</td><td>{e(c)}</td></tr>' for a, b, c in signs)
    return f"""
<section id="transit" class="sec page-break" data-day="0">
  <h2>🚇 交通路網與招牌對照 <small>Transit &amp; Signboard Guide</small></h2>
  <h4>① 廈門地鐵路線代表色速查</h4>
  <table class="zebra"><thead><tr><th>路線</th><th>代表色</th><th>起訖（簡體）</th><th>狀態</th><th>本行程用途</th></tr></thead><tbody>{mrows}</tbody></table>
  <p class="muted">色碼取自維基百科廈門軌道交通模板。沙坡尾附近目前沒有營運中的地鐵站（3 號線南延段施工中），本行程廈門段以計程車／滴滴為主，只有八市可搭 1 號線到「镇海路」。</p>
  <h4>② 城際與泉州交通</h4>
  <table class="zebra"><tbody>
   <tr><td><span class="pill" style="background:#1f6fb2">動車 D</span></td><td>厦门北 → <b>泉州</b>（不是泉州东／泉州南），26–33 分鐘，約 82 班／日。12306 以台胞證購票，刷證進站。</td></tr>
   <tr><td><span class="pill" style="background:#6b7280">泉州無地鐵</span></td><td>古城內以步行、滴滴、「小白」電瓶觀光車（¥2）為主；注意禁行路段的下車點。</td></tr>
   <tr><td><span class="pill" style="background:#0e7490">⛴ 廈鼓航線</span></td><td>東渡郵輪中心 → 內厝澳：每小時 :10 開（08:10–17:10）；內厝澳 → 東渡：每小時 :40（末班 17:40）。普通船往返 ¥35。</td></tr>
   <tr><td><span class="pill" style="background:#7c3aed">🚗 包車</span></td><td>12/26 泉州 → 五店市 → 梧林 → 廈門沙坡尾，估計 ¥400–650。</td></tr>
   <tr><td><span class="pill" style="background:#0f2a44">✈ 機場</span></td><td>去程：高崎 T3（兩岸航班）；回程：翔安新機場（預計）。</td></tr>
  </tbody></table>
  <h4>③ 現場常見簡體指標對照（抬頭就看得懂）</h4>
  <table class="zebra"><thead><tr><th>現場簡體招牌</th><th>意思</th><th>English</th></tr></thead><tbody>{srows}</tbody></table>
  <h4>④ 大陸路牌樣式</h4>
  <p>大陸城市路牌為<b>藍底白字</b>，上排漢字、下排大寫拼音，例如：{street_signs("西街／中山中路／大同路／镇邦路")}</p>
</section>"""

def bookings():
    rows = []
    extra = [
        {"item": "好廳・閩南小館（12/24 平安夜晚餐）", "how": "大眾點評訂位或電話", "link": "", "when": "提前 1–2 週", "notes": "米其林必比登；巷內小院座位少"},
        {"item": "忠記鹽燒番鴨（12/25 晚餐）", "how": "電話 0595-22775083", "link": "", "when": "提前 2–3 天", "notes": "鹽燒需慢煲，先訂可免等"},
        {"item": "南普陀寺入寺預約（12/28）", "how": "微信小程序「南普陀寺预约服务平台」", "link": "", "when": "12/24 起（最多提前 4 天）", "notes": "免費；帶台胞證原件"},
        {"item": "開元寺弘一法師紀念館（選）", "how": "「泉州大开元寺」公眾號／小程序", "link": "", "when": "前 1 天", "notes": "寺院本身免費免預約"},
    ]
    for b in L["bookings"] + extra:
        links = " ".join(f'<a href="{e(u.strip())}">{e(u.strip())}</a>' for u in re.split(r"[；;]", b.get("link") or "") if u.strip().startswith("http"))
        rows.append(f'<tr><td><b>{e(b["item"])}</b></td><td>{e(b["how"])}<br>{links}</td><td>{e(b["when"])}</td><td>{e(fix(b["notes"]))}</td></tr>')
    return f"""
<section id="booking" class="sec page-break" data-day="0">
  <h2>📅 預約與訂位清單 <small>Reservations</small></h2>
  <table class="zebra"><thead><tr><th>項目</th><th>方式／連結</th><th>建議時機</th><th>備註</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
</section>"""

FOODS = [
 ("麵線糊", "面线糊", "泉州早餐之王：細麵線熬成糊，加醋肉、大腸、豬肝、油條。", "羅記（D2）、亞海（D5）", "「一碗面线糊，加醋肉跟大肠，油条剪进去」"),
 ("沙茶麵", "沙茶面", "廈門代表麵食，沙茶湯頭濃郁，按自選配料計價。", "友生（D4）、烏糖（D5）", "「沙茶面，加鱿鱼、猪肝、虾」"),
 ("薑母鴨（鹽燒）", "盐烧姜母鸭", "泉州三派之一：砂鍋加鹽沙慢煲 3–4 小時，冬天最對味。", "忠記（D2）、打漁船（D3）", "「两个人，要半只可以吗？」"),
 ("泉州牛排三件套", "牛排＋牛肉羹＋咸饭", "不是西式牛排，是藥膳香的燉牛肋排，配牛肉羹和鹹飯。", "好成財（D1）", "「A套餐，两份」"),
 ("燒肉粽", "烧肉粽", "閩南肉粽，淋甜辣醬、花生醬、蒜蓉。", "侯阿婆（D2）", "「烧肉粽两个，酱料都要」"),
 ("潤餅", "润饼", "薄皮捲胡蘿蔔絲、高麗菜、豆乾、海蠣與花生糖粉，冬至時節應景。", "亞佛（D2）", "「润饼两卷，要加花生粉」"),
 ("土筍凍", "土笋冻", "沙蟲熬成的晶凍，蘸蒜蓉醋、芥末。", "八市惠林（D4）", "「土笋冻一份，酱料多一点」"),
 ("海蠣煎", "海蛎煎", "海蠣多、粉漿少，比台灣蚵仔煎更「料多」。", "蓮歡（D4）", "「海蛎煎一份，辣酱另放」"),
 ("花生湯", "花生汤", "花生燉到入口即化，配油條或加蛋。", "黃則和（D4）", "「鸡蛋花生汤一碗」（先儲值店卡）"),
 ("石花膏／四果湯", "石花膏／四果汤", "百年老字號甜品；12 月偏涼可請店家少冰。", "秉正堂（D1）", "「石花膏，少冰」"),
]
def foods():
    rows = "".join(f'<tr><td><b>{e(a)}</b><br><span class="signboard sm">{e(b)}</span></td><td>{e(c)}</td><td>{e(d)}</td><td class="simp">{e(f)}</td></tr>' for a, b, c, d, f in FOODS)
    return f"""
<section id="food" class="sec page-break" data-day="0">
  <h2>🍜 閩南美食圖鑑與點餐指南 <small>Food Guide</small></h2>
  <table class="zebra"><thead><tr><th>美食（現場簡體）</th><th>特色</th><th>本行程在哪吃</th><th>點餐話術（直接念）</th></tr></thead><tbody>{rows}</tbody></table>
  <div class="box"><h4>在地用餐文化</h4><ul>
   <li>小吃店多是「先點單付款、拿號碼取餐」，掃支付寶／微信付款最快。</li>
   <li>八市海鮮加工：可在攤位自己挑海鮮再拿去加工店（先講好加工費、按斤或按隻計價），也可直接在店裡點。<b>下單前一定先問清楚單價</b>，避免秤重糾紛。</li>
   <li>不用給小費；「打包」＝外帶，「微辣／不要辣」＝小辣／不辣。</li>
   <li>米其林必比登小館（好廳、羅記、忠記）多是在地老店，人均 ¥20–100。</li>
  </ul></div>
</section>"""

def practical():
    P = L["practical"]
    def flat(v):
        if isinstance(v, dict):
            return "<ul>" + "".join(f"<li><b>{e(k)}：</b>{flat(vv)}</li>" for k, vv in v.items()) + "</ul>"
        if isinstance(v, list):
            return "<ul>" + "".join(f"<li>{flat(i)}</li>" for i in v) + "</ul>"
        return e(fix(v).replace("【未驗證】", "（未核實）").replace("【未驗證", "（未核實").replace("】", "）"))
    blocks = "".join(f'<div class="box"><h4>{e(k.replace("_", " "))}</h4>{flat(v)}</div>' for k, v in P.items())
    return f"""
<section id="practical" class="sec page-break" data-day="0">
  <h2>🧳 行前實用須知 <small>Practical Info</small></h2>
  <div class="grid2">{blocks}</div>
</section>"""

def sources():
    srcs = L.get("sources", [])
    lis = "".join(f'<li><a href="{e(s if isinstance(s, str) else s.get("url", ""))}">{e(s if isinstance(s, str) else (s.get("title") or s.get("url")))}</a></li>' for s in srcs[:30])
    return f"""
<section id="sources" class="sec" data-day="0">
  <h2>資料來源與照片授權</h2>
  <p class="muted">查核日期 2026/10/25。照片全部取自 Wikimedia Commons（依各檔案頁 CC 授權，點圖說連結可見作者與授權）；標「示意」者為同類菜餚，非該店本身。</p>
  <ul class="srcs">{lis}</ul>
</section>"""

# ---------------------------------------------------------------- CSS
CSS = r"""
:root{--navy:#0f2a44;--brick:#b5532f;--gold:#b08d3c;--ink:#1f2937;--paper:#fbf8f3}
*{box-sizing:border-box}
body{font-family:"Noto Sans TC","Microsoft JhengHei",sans-serif;color:var(--ink);background:var(--paper);margin:0;line-height:1.6}
h1,h2,h3,h4{font-family:"Noto Serif TC","PMingLiU",serif;color:var(--navy);margin:.4em 0}
h2{font-size:1.6rem;border-bottom:3px solid var(--brick);padding-bottom:.25rem}
h2 small{font-family:Georgia,serif;font-size:.85rem;color:var(--gold);letter-spacing:.08em;margin-left:.5rem}
a{color:#1f6fb2}
.wrap{max-width:1080px;margin:0 auto;padding:0 16px}
.sec,.day{margin:28px 0}
.hero{position:relative;color:#fff;min-height:380px;display:flex;align-items:flex-end;background:#0f2a44 center/cover no-repeat}
.hero:before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(15,42,68,.15),rgba(15,42,68,.85))}
.hero .in{position:relative;padding:32px 16px;max-width:1080px;margin:0 auto;width:100%}
.hero h1{color:#fff;font-size:2.4rem;margin:0}
.hero p{margin:.3rem 0;opacity:.95}
.kick{letter-spacing:.3em;font-size:.8rem;color:#f3d9a4}
.box{background:#fff;border:1px solid #eadfcd;border-radius:14px;padding:14px 16px;margin:10px 0}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
table{border-collapse:collapse;width:100%;margin:10px 0;font-size:.92rem;background:#fff}
th{background:var(--navy);color:#fff;text-align:left;padding:7px 8px;font-weight:600}
td{padding:7px 8px;border-bottom:1px solid #eee;vertical-align:top}
.zebra tbody tr:nth-child(even) td,.order tbody tr:nth-child(even) td{background:#f6f1e8}
.pill{display:inline-block;color:#fff;border-radius:999px;padding:1px 10px;font-size:.8rem;font-weight:700;white-space:nowrap}
.stcode{background:#eef2f7;border-radius:6px;padding:1px 6px;font-size:.82rem}
.muted{color:#6b7280;font-size:.88rem}
.simp{font-family:"Microsoft YaHei","Noto Sans SC",sans-serif}
.dayhead{display:flex;gap:16px;align-items:flex-start;background:var(--navy);color:#fff;border-radius:16px;padding:16px 18px}
.dayhead h3{color:#fff;margin:.1rem 0;font-size:1.35rem}
.dnum{font-family:Georgia,serif;font-size:1.6rem;font-weight:700;color:#f3d9a4;border:2px solid #f3d9a4;border-radius:12px;padding:4px 10px;white-space:nowrap}
.ddate{margin:0;color:#f3d9a4;font-size:.9rem}
.free{margin:.2rem 0 0;font-size:.9rem;opacity:.9}
.card{background:#fff;border:1px solid #eadfcd;border-left:6px solid var(--brick);border-radius:14px;padding:14px 16px;margin:14px 0}
.ch{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.ch h4{margin:0;font-size:1.15rem;flex:1 1 260px}
.time{font-family:Georgia,serif;font-weight:700;color:var(--brick);min-width:68px}
.badge{color:#fff;font-size:.75rem;border-radius:6px;padding:1px 8px}
.btn{display:inline-block;border-radius:999px;padding:4px 12px;font-size:.85rem;text-decoration:none;font-weight:600}
.amap{background:#e8f1fb;color:#1f6fb2;border:1px solid #bcd5ef}
.info{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:4px 16px;margin:10px 0;font-size:.9rem}
.info dt{font-weight:700;color:var(--navy);font-size:.78rem}
.info dd{margin:0}
.src{font-size:.75rem}
.phs{display:grid;gap:8px;margin:10px 0}
.phs.n2{grid-template-columns:1fr 1fr}
.ph{margin:0}
.ratio{position:relative;width:100%;aspect-ratio:16/10;overflow:hidden;border-radius:10px;background:#eee}
.ratio img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
figcaption{font-size:.78rem;color:#6b7280;margin-top:3px}
.nophoto{font-size:.82rem;color:#8a6d1f;background:#fbf3df;border-radius:8px;padding:6px 10px}
.order th{background:var(--brick)}
.five{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}
.el{display:flex;gap:8px;background:#f8f6f1;border-radius:10px;padding:8px 10px;font-size:.88rem}
.el.wide{grid-column:1/-1}
.el h5{margin:0 0 2px;font-size:.8rem;color:var(--navy)}
.el p{margin:.15rem 0}
.ic{font-size:1.2rem}
.roadsign{display:inline-flex;flex-direction:column;align-items:center;background:#1450a3;color:#fff;border:2px solid #fff;outline:2px solid #1450a3;border-radius:4px;padding:2px 10px;margin:3px 6px 3px 0;line-height:1.15;font-family:"Microsoft YaHei","Noto Sans SC",sans-serif}
.roadsign b{font-size:1rem;letter-spacing:.1em}
.roadsign i{font-style:normal;font-size:.6rem;letter-spacing:.06em}
.signboard{display:inline-block;background:#7a1f12;color:#ffd98a;font-family:"Microsoft YaHei","Noto Sans SC",sans-serif;font-weight:800;font-size:1.05rem;letter-spacing:.12em;padding:3px 12px;border-radius:4px;border:2px solid #c9a24a;margin:2px 0}
.signboard.sm{font-size:.85rem;padding:1px 8px}
.tip{background:#fff6ea;border-radius:10px;padding:8px 10px;margin:8px 0 0;font-size:.9rem}
.note{font-size:.85rem;color:var(--brick);margin:.3rem 0}
.alerts li{margin:.45rem 0}
.srcs{font-size:.78rem;columns:2}
footer{margin:40px 0 20px;text-align:center;color:#6b7280;font-size:.8rem}
@media(max-width:640px){.five{grid-template-columns:1fr}.phs.n2{grid-template-columns:1fr}.hero h1{font-size:1.8rem}.srcs{columns:1}}
"""
WEB_CSS = r"""
nav.glass{position:sticky;top:0;z-index:50;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);background:rgba(251,248,243,.78);border-bottom:1px solid rgba(176,141,60,.3)}
nav .row{display:flex;gap:6px;overflow-x:auto;padding:8px 12px;max-width:1080px;margin:0 auto;scrollbar-width:none}
nav a,nav button{white-space:nowrap}
.cap{border:1px solid var(--navy);background:#fff;color:var(--navy);border-radius:999px;padding:4px 12px;font-size:.85rem;cursor:pointer;font-weight:600}
.cap.on{background:var(--navy);color:#fff}
.cap.lnk{border-color:var(--brick);color:var(--brick);text-decoration:none}
.dl{background:var(--brick);color:#fff;border:none}
.hidden{display:none!important}
.card,.sec,.day{scroll-margin-top:64px}
"""
PRINT_CSS = r"""
@page{size:A4 portrait;margin:12mm 10mm}
*{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{background:#fff;font-size:10.5pt}
.page-break{break-before:page}
.no-break{break-inside:avoid}
.hero{min-height:200mm;border-radius:0}
.hero h1{font-size:30pt}
.ratio{aspect-ratio:2/1}
.phs{grid-template-columns:1fr 1fr;margin:6px 0}
.phs.n1 .ph{max-width:50%}
.card{padding:8px 11px;margin:7px 0;font-size:9.5pt}
.five{gap:5px}.el{padding:5px 8px;font-size:8.8pt}
.info{font-size:8.8pt;margin:6px 0}
table{font-size:8.8pt}
#overview{break-before:page}
.srcs{columns:2}
"""

HEAD = """<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;600;800&family=Noto+Serif+TC:wght@600;800&display=swap" rel="stylesheet">
{tw}<style>{css}</style></head><body>"""

def hero(img="images/yanwu_sunset.jpg"):
    return f"""
<header class="hero" style="background-image:url('{img}')"><div class="in">
 <p class="kick">XIAMEN · QUANZHOU · 2026.12.24 — 12.28</p>
 <h1>{TITLE}</h1>
 <p>5 天 4 夜｜2 位成人（情侶）｜悠閒慢遊｜避開觀光人潮的在地巷弄與老店</p>
 <p>泉州濱江皇冠假日 ×2 晚 → 廈門沙坡尾海景亞朵見野 ×2 晚</p>
</div></header>"""

def body_main():
    return overview() + alerts() + transit() + "".join(day_section(p) for p in PLAN) + bookings() + foods() + practical() + sources()

def build():
    pdf_url = urllib.parse.quote(PDF_NAME)
    caps = '<button class="cap on" data-f="all">全部</button>' + "".join(f'<button class="cap" data-f="{p["day"]}">Day {p["day"]}</button>' for p in PLAN)
    nav = f"""<nav class="glass"><div class="row">{caps}
 <a class="cap lnk" href="#transit">🚇 地鐵招牌對照</a><a class="cap lnk" href="#alerts">⚠️ 必看</a><a class="cap lnk" href="#booking">📅 預約</a><a class="cap lnk" href="#food">🍜 美食</a><a class="cap lnk" href="#practical">🧳 須知</a>
 <a class="cap dl" href="{pdf_url}" download>⬇ 下載 PDF</a></div></nav>"""
    js = """<script>
document.querySelectorAll('nav .cap[data-f]').forEach(b=>b.addEventListener('click',()=>{
 document.querySelectorAll('nav .cap[data-f]').forEach(x=>x.classList.remove('on'));b.classList.add('on');
 const f=b.dataset.f;document.querySelectorAll('main [data-day]').forEach(s=>{
  const d=s.dataset.day;s.classList.toggle('hidden',!(f==='all'||d===f));});
 window.scrollTo({top:document.querySelector('main').offsetTop-60,behavior:'smooth'});}));
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',()=>{
 document.querySelectorAll('main [data-day]').forEach(s=>s.classList.remove('hidden'));
 document.querySelectorAll('nav .cap[data-f]').forEach(x=>x.classList.toggle('on',x.dataset.f==='all'));}));
</script>"""
    web = HEAD.format(t=TITLE, tw='<script src="https://cdn.tailwindcss.com"></script><script>tailwind.config={corePlugins:{preflight:false}}</script>', css=CSS + WEB_CSS) + hero() + nav + \
        f'<main class="wrap">{body_main()}</main><footer>© 2026 私人行程手冊 · 網頁與 PDF 同步產生自 build.py · <a href="{pdf_url}">下載完整 PDF</a></footer>{js}</body></html>'
    open("index.html", "w", encoding="utf-8").write(web)
    toc = "".join(f'<li>Day {p["day"]}｜{e(p["date"])}｜{e(p["title"])}</li>' for p in PLAN)
    pr = HEAD.format(t=TITLE, tw="", css=CSS + PRINT_CSS) + hero() + \
        f'<main class="wrap"><section class="sec"><h2>目錄 <small>Contents</small></h2><ol><li>行程總覽、出發前必看</li><li>交通路網與招牌對照</li>{toc}<li>預約清單、美食圖鑑、行前須知</li></ol>' \
        f'<p class="muted">線上互動版：https://roychihcheng.github.io/xiamen-quanzhou-travel-guide/</p></section>{body_main()}</main></body></html>'
    open("print.html", "w", encoding="utf-8").write(pr)
    print("built", len(web), len(pr))

if __name__ == "__main__":
    build()
