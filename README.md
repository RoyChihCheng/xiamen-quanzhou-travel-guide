# 廈門・泉州 極致奢享深度遊（2026/12/24–12/28）

5 天 4 夜、2 位成人的私人行程手冊：先泉州古城（平日人少）→ 晉江僑鄉包車南下 → 廈門沙坡尾過週末 → 廈門直飛台北。

- 線上互動版（手機適用）：https://roychihcheng.github.io/xiamen-quanzhou-travel-guide/
- 完整 PDF：`廈門泉州極致奢享_深度遊行程規劃指南.pdf`

## 內容
- 每個景點、餐廳、飯店都附交通與招牌對照卡：交通方式、下車點與入口、路牌（藍底白字加拼音）、現場簡體招牌與菜單原文、步行動線
- 高德地圖導航連結（大陸無法使用 Google Maps）
- 廈門地鐵路線代表色、城際動車、廈鼓航線速查，以及常見簡體指標對照
- 預約清單、閩南美食圖鑑與點餐話術、行前須知
- 照片取自 Wikimedia Commons，圖說連到原檔頁面，可查看作者與授權

## 更新方式（網頁與 PDF 必須同步）
```bash
python build.py      # 由 data/*.json 與 build.py 內的 PLAN 產生 index.html + print.html
"C:/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu \
  --run-all-compositor-stages-before-draw --virtual-time-budget=20000 --no-pdf-header-footer \
  --print-to-pdf="廈門泉州極致奢享_深度遊行程規劃指南.pdf" "file:///<repo>/print.html"
git add -A && git commit -m "update" && git push
```

查核日期為 2026/10/25。標示「未核實」的資料只有單一來源或是推估值，出發前請用大眾點評或高德地圖再確認。
