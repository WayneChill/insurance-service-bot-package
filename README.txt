================================================================
  保服小幫手 - 安裝與使用說明
================================================================

【系統說明】
本系統透過 LINE Bot 提供保險業務保全服務管理，功能包含：
・查詢客戶資料與保單（壽險 + 產險）
・開立保服案件（理賠、契變、保費變更）
・追蹤案件進度
・信用卡繳費資訊管理

================================================================
  一、事前準備（首次使用）
================================================================

━━ 1. 安裝 Python ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
前往 https://www.python.org/downloads/
下載最新版 Python（建議 3.12 以上）
安裝時請勾選「Add Python to PATH」（重要！）


━━ 2. 申請 LINE Bot ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 前往 https://developers.line.biz
2. 登入後建立一個 Provider
3. 在 Provider 內建立「Messaging API Channel」
4. 進入 Channel 後：
   - 「Basic settings」頁面 → 複製「Channel secret」
   - 「Messaging API」頁面 → 在最下方「Channel access token」按「Issue」→ 複製 token
5. 關閉「Auto-reply messages」（Messaging API 頁面 → LINE Official Account features）


━━ 3. 設定 Google 服務帳號 ━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 前往 https://console.cloud.google.com
2. 建立新專案（或使用現有專案）
3. 左側選單 → 「API 和服務」→「程式庫」
   搜尋並啟用以下兩個 API：
   ✓ Google Sheets API
   ✓ Google Drive API
4. 左側選單 → 「API 和服務」→「憑證」
   → 「建立憑證」→「服務帳號」→ 填入名稱後建立
5. 點剛建立的服務帳號 → 「金鑰」標籤 → 「新增金鑰」→「JSON」
   → 下載 JSON 檔，改名為 credentials.json，放入本資料夾
6. 記下服務帳號的 Email（格式：xxx@xxx.iam.gserviceaccount.com）


━━ 4. 建立 Google 試算表（案件記錄用）━━━━━━━━━━━━━━━
1. 前往 https://sheets.google.com，建立新試算表
2. 右上角「共用」→ 輸入服務帳號 Email → 權限選「編輯者」→ 確定
3. 從試算表網址複製 ID（網址中 /d/ 和 /edit 之間的字串）
   例：https://docs.google.com/spreadsheets/d/【這裡是ID】/edit
（工作表欄位會在首次啟動時自動建立，不需手動設定）


━━ 5. 建立 Google Drive 資料夾（Excel 保單資料用）━━━━━
1. 前往 https://drive.google.com，建立名為「保服資料」的資料夾
   （資料夾名稱必須完全一致）
2. 右鍵資料夾 → 「共用」→ 輸入服務帳號 Email → 「編輯者」→ 確定
3. 將以下兩個 Excel 保單檔上傳至此資料夾：
   ✓ 42003.xlsx（壽險資料）
   ✓ 42004.xlsx（產險資料）


━━ 6. 填寫設定檔 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
用記事本開啟 config.txt，填入以下資料：

  LINE_CHANNEL_ACCESS_TOKEN → 步驟 2 取得的 Channel access token
  LINE_CHANNEL_SECRET       → 步驟 2 取得的 Channel secret
  GOOGLE_CREDENTIALS_FILE   → credentials.json（通常不用改）
  GOOGLE_SHEET_ID           → 步驟 4 取得的試算表 ID
  LICENSE_KEY               → 向系統提供者取得的授權金鑰


━━ 7. 填入授權金鑰 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
用記事本開啟 license.txt，填入向管理員取得的授權金鑰


================================================================
  二、安裝套件
================================================================

雙擊執行 setup.bat，等待安裝完成（約 1-3 分鐘）


================================================================
  三、部署到 Railway（必要步驟）
================================================================

【重要】保服小幫手是常駐伺服器，不像產險助手可以手動執行。
必須部署到 Railway 才能透過 LINE 收發訊息。

部署步驟：

1. 前往 https://github.com，新建一個私人 Repository
   將本資料夾的所有檔案（除了 credentials.json）推送上去
   （確認 .gitignore 已排除 credentials.json）

2. 前往 https://railway.app 註冊並建立新專案
   → 「Deploy from GitHub repo」→ 選擇剛建立的 Repository

3. 在 Railway 的 Variables（環境變數）設定以下項目：
   LINE_CHANNEL_ACCESS_TOKEN → 同 config.txt
   LINE_CHANNEL_SECRET       → 同 config.txt
   GOOGLE_SHEET_ID           → 同 config.txt
   LICENSE_KEY               → 同 config.txt / license.txt
   GOOGLE_CREDENTIALS_B64    → 見下方說明

   【取得 GOOGLE_CREDENTIALS_B64】
   在本資料夾執行以下指令（PowerShell）：
   python -c "import base64; print(base64.b64encode(open('credentials.json','rb').read()).decode())"
   複製輸出的字串貼入 Railway 環境變數

4. 部署成功後，在 Railway 的 Settings → Networking → Generate Domain
   取得你的網址（例：https://xxx.up.railway.app）

5. 前往 LINE Developers → 你的 Channel → Messaging API
   將 Webhook URL 設為：https://xxx.up.railway.app/callback
   開啟「Use webhook」


================================================================
  四、LINE 指令說明
================================================================

【查詢客戶】
  查詢 王小明         → 顯示客戶資料、保單、信用卡

【案件管理】
  進度 王小明         → 查看保服案件進度
  （在客戶卡片上點「理賠」「契變」「保費變更」可直接開案）

【信用卡管理】
  新增卡片 王小明 國泰世華 5678 12/27          → 新增信用卡（所有保單）
  新增卡片 王小明 國泰世華 5678 12/27 保單號碼  → 新增信用卡（指定保單）
  刪除卡片 王小明 國泰世華 5678               → 刪除信用卡

【其他】
  說明 / help / ?     → 顯示指令說明與待處理案件


================================================================
  五、常見問題
================================================================

Q：LINE 收不到回覆？
A：確認 Webhook URL 設定正確、Railway 部署成功（無報錯）

Q：查詢客戶找不到資料？
A：確認 Google Drive「保服資料」資料夾中有 42003.xlsx 和 42004.xlsx
   且服務帳號已被分享編輯權限

Q：顯示「金鑰驗證失敗」？
A：確認 LICENSE_KEY 填寫正確，或聯絡系統提供者確認金鑰狀態

Q：Google Sheets 寫入失敗？
A：確認試算表已共用給服務帳號，且 GOOGLE_SHEET_ID 填寫正確

================================================================
  如需技術支援，請聯絡系統提供者
================================================================
