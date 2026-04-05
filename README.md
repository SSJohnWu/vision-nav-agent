# Vision-Aided AR Navigation Agent

智慧視障輔助導航系統，使用 OpenCV + OpenClaw AI Agent 為視障者與銀髮族提供環境感知與安全導航。

## 特色

- 🎥 即時影像障礙物偵測
- 🗣️ 簡潔語音指令導航
- 🧠 OpenClaw AI 決策大腦
- ♿ 極具社會公益價值

## 專案架構

```
vision-nav-agent/
├── src/
│   ├── agent/         # OpenClaw Agent 核心
│   ├── vision/        # OpenCV 影像處理
│   ├── audio/         # 語音合成/辨識
│   ├── navigation/    # 路徑規劃模組
│   └── utils/         # 工具函式
├── config/            # 設定檔
├── models/            # AI 模型
├── tests/             # 單元測試
└── docs/              # 文件
```

## 快速開始

### 1. 確保本地大腦 (OpenClaw Server) 已啟動
本系統採用**前端微服務架構**。執行之前，請先確認您的本地端 OpenClaw 伺服器 (基於 Ollama) 已經啟動，系統預設的連線端點為：
`http://127.0.0.1:18789`

*(若您的伺服器 IP 或 Port 不同，請至 `config/config.yaml` 進行修改)*

### 2. 安裝套件與執行程式
啟動您的虛擬環境並安裝所需依賴。
本專案提供兩種體驗模式：**「電腦端直接除錯版」** 與 **「戶外移動端 Web App 版」**。

```bash
pip install -r requirements.txt

# [模式A] 在電腦端開啟視窗與喇叭直接測試：
python src/main.py

# [模式B] 啟動行動版本機網路伺服器 (供手機遠端當作攝影機與發聲機)：
python src/web_main.py
```

### 3. 移動端與戶外連線教學
若您採用了 **[模式B]** 啟動網路伺服器，因手機瀏覽器限制使用鏡頭必須為安全連線 (HTTPS)，請另開一個終端機，利用 `ngrok` 工具將本機的 `8000` 埠口穿透出去：
```bash
ngrok http 8000
```
最後，將 `ngrok` 給出的 `https://...` 臨時網址輸入至您的智慧型手機瀏覽器中，按下畫面上大大的「啟動導航」，系統就會變成您的專屬行動導航犬了！

### 終止程式

按 `Ctrl+C` 或關閉終端機即可停止。

### 切換外接鏡頭 / 網路攝影機

系統支援 USB 外接鏡頭或無線網路攝影機（如手機 App 串流、IP Camera）。請開啟 `config/config.yaml` 檔案修改：

**1. 使用 USB 外接鏡頭**
預設內建鏡頭為 `0`，外接鏡頭請改為 `1` 或 `2`：
```yaml
camera:
  index: 1  
```

**2. 使用網路攝影機 (RTSP / HTTP 串流)**
您可以直接將 `index` 的值替換為含引號的網址字串：
```yaml
camera:
  index: "rtsp://username:password@192.168.1.100/stream" 
  # 或者 "http://192.168.1.50:8080/video"
```

設定存檔後，再次啟動主程式即會自動連線。

## 使用情境

- 視障者室內/室外導航
- 銀髮族輔助行走
- 未來 AR 裝置整合
