================================================================
保險業務發展小幫手 LINE Bot
安裝說明（完整版）
================================================================

本說明適合完全沒有程式基礎的使用者。
請依照順序一步一步完成，不要跳過任何步驟。

預計完成時間：約 60～90 分鐘

================================================================
【第一步：準備需要的帳號】
================================================================

你需要以下帳號，沒有的請先註冊：

① LINE Official Account（LINE 官方帳號）
   申請網址：https://www.linebiz.com/tw/
   點「立即開始」→ 用你的 LINE 帳號登入 → 建立帳號

② LINE Developers（LINE 開發者）
   網址：https://developers.line.biz
   用同一個 LINE 帳號登入即可

③ Google 帳號（有 Gmail 就可以用）

④ GitHub 帳號
   申請網址：https://github.com
   免費註冊

⑤ Railway（雲端伺服器）
   申請網址：https://railway.app
   點「Start a New Project」→ 用 GitHub 帳號登入

⑥ 授權金鑰
   聯絡 Wayne 取得，拿到一串英數字備用


================================================================
【第二步：設定 LINE Official Account】
================================================================

① 登入 LINE Official Account Manager
   網址：https://manager.line.biz
   選你的帳號

② 開啟 Webhook
   左側選「聊天」→「回應設定」
   「回應模式」選「Bot」
   「Webhook」打開（開關變綠色）
   「自動回應訊息」關閉

③ 取得 Channel Access Token
   到 LINE Developers：https://developers.line.biz
   點你的帳號 → 點「Messaging API」頁籤
   往下找「Channel access token」→ 點「Issue」
   複製這串字 → 存到記事本，標記為【Token】

④ 取得 Channel Secret
   同一個頁面往上找「Channel secret」
   複製這串字 → 存到記事本，標記為【Secret】

⑤ 取得你的 LINE User ID
   同一個頁面找「Your user ID」
   複製 U 開頭那串字 → 存到記事本，標記為【UserID】


================================================================
【第三步：建立 Google 服務帳號】
================================================================

① 進入 Google Cloud Console
   網址：https://console.cloud.google.com
   用 Google 帳號登入

② 建立專案
   上方點「選取專案」→「新增專案」
   名稱填「insurance-bot」→ 點「建立」

③ 啟用 Google Sheets API
   左側選「API 和服務」→「程式庫」
   搜尋「Google Sheets API」→ 點進去 → 點「啟用」

④ 啟用 Google Drive API
   搜尋「Google Drive API」→ 點進去 → 點「啟用」

⑤ 建立服務帳號
   左側選「IAM 與管理」→「服務帳號」
   點「+ 建立服務帳號」
   名稱填「insurance-bot」→ 點「建立並繼續」
   角色選「編輯者」→ 點「繼續」→ 點「完成」

⑥ 下載金鑰
   點剛建立的服務帳號
   點「金鑰」頁籤 → 點「新增金鑰」→「建立新金鑰」
   選「JSON」→ 點「建立」
   瀏覽器會自動下載一個 .json 檔案
   把這個檔案重新命名為「credentials.json」

⑦ 複製服務帳號 Email
   回到服務帳號列表
   複製 Email 欄位（格式：xxx@xxx.iam.gserviceaccount.com）
   存到記事本，標記為【ServiceEmail】


================================================================
【第四步：建立 Google 試算表】
================================================================

① 到 Google 試算表：https://sheets.google.com
   點「空白」建立新試算表
   名稱改為「保險業務發展小幫手」

② 複製試算表 ID
   看網址列：
   https://docs.google.com/spreadsheets/d/【這裡就是ID】/edit
   複製中間那串字 → 存到記事本，標記為【SheetsID】

③ 共用給服務帳號
   右上角點「共用」
   貼上【ServiceEmail】
   權限選「編輯者」
   取消勾選「通知使用者」
   點「共用」


================================================================
【第五步：建立 Google Drive 資料夾】
================================================================

① 到 Google 雲端硬碟：https://drive.google.com

② 建立新資料夾
   點「+ 新增」→「新增資料夾」
   名稱填「保服資料」→ 點「建立」

③ 上傳保單 Excel 檔
   點進「保服資料」資料夾
   上傳你的壽險保單（42003.xlsx）和產險保單（42004.xlsx）

④ 複製資料夾 ID
   進入資料夾後看網址列：
   https://drive.google.com/drive/folders/【這裡就是ID】
   複製 → 存到記事本，標記為【DriveID】

⑤ 共用給服務帳號
   對「保服資料」資料夾按右鍵 → 點「共用」
   貼上【ServiceEmail】
   權限選「編輯者」
   取消勾選「通知使用者」
   點「共用」


================================================================
【第六步：填寫設定檔】
================================================================

① 打開捆包資料夾，找到「config.txt」
   用記事本打開

② 把每個欄位填好：

   LINE_CHANNEL_ACCESS_TOKEN = 填入【Token】
   LINE_CHANNEL_SECRET       = 填入【Secret】
   LINE_USER_ID              = 填入【UserID】
   GOOGLE_SHEET_ID           = 填入【SheetsID】
   DRIVE_FOLDER_ID           = 填入【DriveID】
   LICENSE_KEY               = 填入 Wayne 給的金鑰

③ 存檔

④ 把「credentials.json」放入捆包資料夾（和 config.txt 同一層）


================================================================
【第七步：部署到 Railway】
================================================================

① 到 GitHub 建立新 repo
   到 https://github.com 登入
   點右上角「+」→「New repository」
   名稱填「my-insurance-bot」
   選「Private」→ 點「Create repository」

② 上傳檔案到 GitHub
   進入新建立的 repo
   點「uploading an existing file」
   把捆包資料夾裡所有檔案一次拖進去
   包含：app.py, sheets.py, excel_reader.py, flex_message.py,
         scheduler.py, requirements.txt, Procfile, Dockerfile,
         config.txt, credentials.json, license.txt
   點「Commit changes」

③ 到 Railway 部署
   到 https://railway.app 登入
   點「New Project」→「Deploy from GitHub repo」
   選「my-insurance-bot」

④ 設定環境變數
   點進你的服務 → 點「Variables」頁籤
   逐一新增以下環境變數（名稱 = 值）：

   LINE_CHANNEL_ACCESS_TOKEN = 【Token】
   LINE_CHANNEL_SECRET       = 【Secret】
   LINE_USER_ID              = 【UserID】
   GOOGLE_SHEET_ID           = 【SheetsID】
   DRIVE_FOLDER_ID           = 【DriveID】
   LICENSE_KEY               = Wayne 給的金鑰

   ★ 特別重要：credentials.json 要轉成 base64
     打開 PowerShell（開始 → 搜尋 PowerShell）
     輸入以下指令（路徑換成你實際的位置）：
     [Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Users\你的名字\Downloads\credentials.json"))
     複製輸出的長字串
     在 Railway 新增變數：GOOGLE_CREDENTIALS_B64 = 剛才複製的長字串

⑤ 等待部署完成
   看到綠色「Deployment successful」就完成了
   記下你的 Railway 網址（格式：xxx.railway.app）


================================================================
【第八步：設定 LINE Webhook】
================================================================

① 到 LINE Developers：https://developers.line.biz
   點你的帳號 → 點「Messaging API」頁籤

② 找到「Webhook URL」→ 點「Edit」

③ 填入：
   https://【你的Railway網址】/callback
   例如：https://my-insurance-bot.railway.app/callback

④ 點「Update」→ 點「Verify」
   出現「Success」就完成了


================================================================
【完成！測試看看】
================================================================

打開 LINE，找到你的官方帳號，發送以下訊息：

「說明」→ 應該出現指令列表卡片
「早報」→ 應該出現今日待辦
「產險」→ 應該出現產險到期卡片

有問題請聯絡 Wayne。


================================================================
【常用指令一覽】
================================================================

查詢 姓名                查看客戶資料和保單
進度 姓名                查看保服案件進度
早報                     手動觸發今日早報
保服                     待處理保服案件列表
待辦                     今日全部待辦彙整
產險                     產險60天內到期卡片
壽險                     今日壽星＋保單周年名單
業務                     業務追蹤列表
增員                     增員追蹤列表
新增業務 姓名 電話 階段   階段：已聯繫/建議書/約簽約/送保單
新增增員 姓名 電話 階段   階段：已聯繫/約聊聊/約簽約
更新業務 ID 階段          例：更新業務 B001 建議書
更新增員 ID 階段          例：更新增員 R001 約聊聊
新增卡片 姓名 銀行 卡號前4碼 效期
刪除卡片 姓名 銀行 卡號前4碼
說明                     顯示此說明

每天早上 8:00 自動推播每日早報。

================================================================
如有問題請聯絡 Wayne
================================================================
