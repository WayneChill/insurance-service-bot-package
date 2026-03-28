================================================================
保險業務發展小幫手 LINE Bot
版本：v1.0.0
安裝說明（完整版）
================================================================

本說明適合完全沒有程式基礎的使用者。
請依照順序一步一步完成，不要跳過任何步驟。

預計完成時間：約 60～90 分鐘

================================================================
【費用說明】
================================================================

使用本系統每月需要支付以下費用：

① Railway 伺服器費用
   每月 $5 美元（約新台幣 160 元）
   → 需要綁定信用卡（VISA / MasterCard 皆可）
   → 每月自動扣款
   → 這是唯一需要付費的服務

② 其他服務（以下皆免費）
   → Google 帳號：免費
   → Google Sheets：免費
   → Google Drive：免費
   → GitHub：免費
   → LINE Official Account：免費（基本方案）
   → 授權金鑰：依與 Wayne 的約定

總計：每月約 $5 美元 + 授權金鑰費用


================================================================
【安全性說明】
================================================================

★ 請務必閱讀以下安全注意事項 ★

① 授權金鑰安全
   → 金鑰已綁定你的 LINE Channel Secret，其他人即使拿到你的金鑰也無法使用
   → 請勿將金鑰分享給任何人，分享後你的帳號可能被停用
   → 金鑰有使用期限，到期前請聯絡 Wayne 續期

② Google 憑證安全（最重要！）
   → credentials.json 是你的 Google 服務帳號金鑰
   → 這個檔案擁有讀取你所有 Google 試算表和雲端硬碟的權限
   → ！絕對不能把這個檔案傳給任何人！
   → ！不能上傳到公開的 GitHub（請選 Private repo）！
   → ！不能用 LINE 或 Email 傳送給他人！
   → 如果不小心外洩，請立刻到 Google Cloud Console 刪除並重新產生

③ GitHub Repo 安全
   → 建立 GitHub repo 時，一定要選「Private（私人）」
   → Public（公開）repo 任何人都能看到你的設定和程式碼
   → credentials.json 和 config.txt 裡有敏感資料，絕對不能公開

④ 關於程式碼破解風險
   → 本系統使用授權金鑰保護，但有技術能力的人（或透過 AI 工具）
     理論上可以修改程式碼繞過驗證
   → 若發現有人非法使用，請立刻聯絡 Wayne 停用相關金鑰
   → 非法使用授權軟體可能涉及法律責任

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

   ★ 重要：取得授權金鑰前，你必須先提供以下資料給 Wayne：
     → 你的 LINE Channel Secret（取得方式見第二步④）
     → Wayne 會用這個資料把金鑰綁定到你的帳號
     → 金鑰一旦綁定就無法轉讓給他人使用


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

④ 取得 Channel Secret（★ 這個要傳給 Wayne 才能取得授權金鑰）
   同一個頁面往上找「Channel secret」
   右邊點「Copy」複製這串字
   → 存到記事本，標記為【Secret】
   → 同時把這串字傳給 Wayne，Wayne 才能幫你產生專屬金鑰

   ！注意：Channel Secret 是你帳號的識別碼
           金鑰會綁定這串字，別人拿到你的金鑰也無法使用
           請不要把 Channel Secret 分享給不認識的人

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

   ★ 關於授權金鑰：
     - 金鑰格式像這樣：XXXX-XXXX-XXXX-XXXX
     - 金鑰已綁定你的 LINE Channel Secret，無法給其他人使用
     - 金鑰有使用期限，到期前請聯絡 Wayne 續期
     - 請妥善保管，不要把金鑰分享給任何人

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
   LICENSE_KEY               = Wayne 給的金鑰（格式：XXXX-XXXX-XXXX-XXXX）

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
【版本更新說明】
================================================================

目前版本：v1.0.0（2026/03/28 發布）

更新內容：
v1.0.0 - 初始版本
  → 合併產險助手 + 保服助手
  → 新增業務追蹤、增員追蹤功能
  → 每日 08:00 自動推播早報
  → 圖文選單六宮格
  → 授權金鑰綁定 LINE Channel Secret

================================================================
【如何更新到最新版本】
================================================================

當 Wayne 發布新版本時，你會收到通知。更新步驟如下：

① 下載最新捆包
   → 到 GitHub 下載最新版本
   → https://github.com/WayneChill/insurance-service-bot-package

② 比對有哪些檔案更新
   → Wayne 會告知哪些檔案有變動

③ 更新 GitHub repo
   → 到你的 GitHub（my-insurance-bot）
   → 把更新的檔案一一上傳覆蓋舊版

④ Railway 自動重新部署
   → 上傳完成後 Railway 會自動偵測並重新部署
   → 約 2 分鐘後完成

⑤ 測試確認
   → 發送「說明」給 Bot 確認正常運作

！注意：更新不會影響你的資料（Google Sheets 的資料不會被清除）


================================================================
【取得授權金鑰的完整流程】
================================================================

在安裝之前，你需要先向 Wayne 取得授權金鑰。
金鑰會綁定你的 LINE 帳號，確保只有你能使用。

步驟一：先完成第二步，取得你的 Channel Secret
   → Channel Secret 是一串 32 碼的英數字
   → 在 LINE Developers → Messaging API 頁面可以找到

步驟二：把以下資料傳給 Wayne
   ① 你的姓名（或公司名稱）
   ② 你的 LINE Channel Secret【Secret】
   → 可以用 LINE 私訊、Email 或任何方式傳給 Wayne

步驟三：Wayne 會幫你產生專屬金鑰
   → 金鑰格式：XXXX-XXXX-XXXX-XXXX
   → 金鑰有效期限依雙方約定
   → 金鑰綁定你的 Channel Secret，無法轉讓他人

步驟四：收到金鑰後
   → 填入 config.txt 的 LICENSE_KEY 欄位
   → 填入 Railway 環境變數的 LICENSE_KEY

！注意事項：
   - 金鑰只能搭配你提供的 Channel Secret 使用
   - 如果你重新建立 LINE OA（Channel Secret 會改變），
     需要通知 Wayne 重新綁定
   - 金鑰到期前 7 天請聯絡 Wayne 續期，否則 Bot 會停止運作
   - 請勿將金鑰分享給他人，分享後你的帳號可能被停用


================================================================
如有問題請聯絡 Wayne
================================================================
