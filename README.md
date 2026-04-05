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
啟動您的虛擬環境，安裝客戶端所需的影像與語音依賴套件，並啟動助理：

```bash
pip install -r requirements.txt
python src/main.py
```

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
