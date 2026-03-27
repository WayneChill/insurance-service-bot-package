@echo off
chcp 65001 > nul
echo ================================================
echo  保服小幫手 - 一鍵安裝
echo ================================================
echo.

:: 確認 Python 是否已安裝
python --version > nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 Python，請先從 https://www.python.org 下載安裝
    echo        安裝時請勾選「Add Python to PATH」
    pause
    exit /b 1
)

echo [1/3] 正在安裝必要套件（約需 1-3 分鐘）...
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo [錯誤] 套件安裝失敗，請檢查網路連線後重試
    pause
    exit /b 1
)
echo       套件安裝完成 ✓

echo.
echo [2/3] 確認設定檔...

if not exist "config.txt" (
    echo [錯誤] 找不到 config.txt
    pause
    exit /b 1
)
echo       config.txt 存在 ✓

if not exist "license.txt" (
    echo [錯誤] 找不到 license.txt
    pause
    exit /b 1
)
echo       license.txt 存在 ✓

echo.
echo [3/3] 確認憑證檔...
for /f "tokens=2 delims==" %%a in ('findstr "GOOGLE_CREDENTIALS_FILE" config.txt') do set CREDS=%%a
set CREDS=%CREDS: =%
if not exist "%CREDS%" (
    echo [警告] 找不到憑證檔 %CREDS%
    echo        請將 Google 服務帳號 JSON 檔放入本資料夾，並在 config.txt 填入檔名
) else (
    echo       憑證檔存在 ✓
)

echo.
echo ================================================
echo  安裝完成！部署步驟請參閱 README.txt
echo ================================================
echo.
pause
