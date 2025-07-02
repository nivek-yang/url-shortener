<p align="center">
  <img src="backend/static/assets/images/shr_logo.png" alt="shr.today logo" width="120">
</p>


# 專案介紹

本專案是一個短網址服務 [https://shr.today](https://shr.today)，使用 Django 開發，支援 Google OAuth 登入、密碼保護短網址、自動抓取網頁資訊、短網址管理等服務。

---

## 主要功能

- **縮網址服務**：快速產生短網址，支援自訂 slug。
- **密碼保護**：可為短網址設定密碼，需輸入正確密碼才能跳轉。
- **自動抓取頁面資訊**：一鍵取得原始網址的標題與描述，自動填入備註欄。
- **Google OAuth 登入**：整合 django-allauth，支援 Google 帳號登入。
- **短網址管理**：登入後可檢視、編輯、刪除自己建立的短網址。
- **複製短網址**：一鍵複製短網址到剪貼簿。
- **即時訊息提示**：所有操作皆有明確的成功/錯誤提示，訊息自動消失。
- **現代化 UI**：採用 Tailwind CSS、DaisyUI 與 Font Awesome。

---

## 技術棧

- **後端**：Django、django-allauth、PostgreSQL、requests、BeautifulSoup4
- **前端**：Alpine.js、Tailwind CSS、DaisyUI
- **部署**：Docker、Nginx、GCP
- **自動化測試**：pytest、github actions

---

## 專案架構

```
url-shortener/
├── backend/                  # 後端開發資料夾
│   ├── config/               # 專案設定 (settings.py, urls.py)
│   ├── links/                # 短網址核心功能的 App
│   ├── pages/                # 處理靜態頁面 (如首頁) 的 App
│   ├── static/               # 靜態檔案 (CSS, JS, Images)
│   └── manage.py
├── frontend/                 # 前端模板與 JS
│   ├── templates/            # Django 模板
│   │   ├── layouts/
│   │   ├── links/
│   │   ├── pages/
│   │   └── shared/
│   └── src/                  # 前端 JS 原始碼
│       └── scripts/
├── .env.example              # 環境變數
├── .gitignore
├── docker-compose.prod.yml   # Docker 部署設定
├── docker-compose.dev.yml
├── Dockerfile         
└── README.md
```

## 主要加強內容

- 新增 API 支援，方便第三方整合
- 增強短網址安全性（如防止濫用、黑名單機制）
- 提供更詳細的短網址統計報表
- 支援多語系介面
- 前後端效能優化
- 更多自訂化選項（如短網址有效期限、批次產生等）