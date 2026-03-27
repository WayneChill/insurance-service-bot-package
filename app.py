import os
import sys
import json
import urllib.request
import urllib.error
import gspread
from datetime import datetime

# ===== 讀取 config.txt（Railway 環境變數優先）=====
def _read_config():
    config = {}
    if os.path.exists("config.txt"):
        with open("config.txt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    config[k.strip()] = v.strip()
    return config

_cfg = _read_config()
for _k, _v in _cfg.items():
    if _k not in os.environ:
        os.environ[_k] = _v

# ===== 授權金鑰驗證 =====
VERIFY_URL = "https://insurance-service-bot-production.up.railway.app/verify-key"

def _get_license_key():
    key = os.environ.get("LICENSE_KEY", "").strip()
    if key and "請填入" not in key:
        return key
    if os.path.exists("license.txt"):
        with open("license.txt", encoding="utf-8") as f:
            key = f.read().strip()
        if key and "請填入" not in key:
            return key
    return ""

def _verify_license():
    key = _get_license_key()
    if not key:
        print("❌ 未提供授權金鑰，請在 license.txt 或 LICENSE_KEY 環境變數中填入金鑰")
        return False
    try:
        data = json.dumps({"key": key}).encode("utf-8")
        req = urllib.request.Request(
            VERIFY_URL, data=data,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        if result.get("valid"):
            print(f"✅ 授權金鑰驗證成功（{result.get('user', '')}，有效至 {result.get('expiry', '')}）")
            return True
        else:
            print(f"❌ {result.get('message', '金鑰驗證失敗')}")
            return False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"❌ 授權伺服器錯誤 HTTP {e.code}：{body[:200]}")
        return False
    except Exception as e:
        print(f"❌ 無法連線到授權伺服器：{e}")
        return False

if not _verify_license():
    sys.exit(1)

# ===== 主程式 =====
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, PostbackEvent
from urllib.parse import unquote
from excel_reader import search_client
from case_manager import CaseManager
from flex_message import build_client_card, build_help_message, build_cases_card

app = Flask(__name__)
line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])
case_mgr = CaseManager()

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    print('RECEIVED', body[:80], flush=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return str(e), 500
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    reply = parse_command(text)
    if reply['type'] == 'flex':
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text=reply['alt'], contents=reply['contents'])
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply['text'])
        )

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    params = dict(p.split('=', 1) for p in data.split('&') if '=' in p)
    action = params.get('action', '')
    name = unquote(params.get('name', ''))
    policy = unquote(params.get('policy', ''))

    service_types = ['理賠', '契變', '保費變更']
    if action in service_types:
        case_id = case_mgr.add_case(name, action, policy)
        msg = (
            '✅ 已開立案件 #' + case_id + '\n'
            '客戶：' + name + '\n'
            '項目：' + action + '\n\n'
            '輸入「進度 ' + name + '」查看進度'
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
    elif action == 'update':
        case_id = unquote(params.get('id', ''))
        status = unquote(params.get('status', ''))
        case_mgr.update_status(case_id, status)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='✅ 案件 #' + case_id + ' 已更新為「' + status + '」')
        )
    elif action == 'check_cases':
        cases = case_mgr.get_cases(name)
        contents = build_cases_card(name, cases)
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text='保服進度：' + name, contents=contents)
        )

def parse_command(text):
    parts = text.split()
    cmd = parts[0] if parts else ''

    if cmd == '查詢' and len(parts) >= 2:
        name = parts[1]
        print('Searching: ' + name, flush=True)
        result = search_client(name)
        if not result:
            return {'type': 'text', 'text': '❌ 找不到「' + name + '」的資料\n請確認姓名是否正確'}
        cards = case_mgr.get_cards(name)
        contents = build_client_card(result, name, cards)
        return {'type': 'flex', 'alt': '客戶資料：' + name, 'contents': contents}

    elif cmd == '進度' and len(parts) >= 2:
        name = parts[1]
        cases = case_mgr.get_cases(name)
        return {'type': 'flex', 'alt': '保服進度：' + name, 'contents': build_cases_card(name, cases)}

    elif cmd == '新增卡片' and len(parts) >= 5:
        c_name = parts[1]
        c_bank = parts[2]
        c_num = parts[3]
        c_exp = parts[4]
        c_policy = parts[5] if len(parts) >= 6 else ''
        case_mgr.add_card(c_name, c_bank, c_num, c_exp, c_policy)
        note = '（指定保單：' + c_policy + '）' if c_policy else '（所有保單）'
        return {'type': 'text', 'text': '✅ 已新增信用卡\n姓名：' + c_name + '\n銀行：' + c_bank + '\n卡號：' + c_num + '\n效期：' + c_exp + '\n' + note}

    elif cmd == '刪除卡片' and len(parts) >= 4:
        c_name = parts[1]
        c_bank = parts[2]
        c_num = parts[3]
        success = case_mgr.delete_card(c_name, c_bank, c_num)
        if success:
            return {'type': 'text', 'text': '✅ 已刪除「' + c_name + '」 ' + c_bank + ' ' + c_num + ' 的信用卡'}
        return {'type': 'text', 'text': '❌ 找不到該信用卡'}

    elif cmd in ['說明', 'help', '?']:
        all_pending = case_mgr.get_all_pending()
        contents = build_help_message(all_pending)
        return {'type': 'flex', 'alt': '指令說明', 'contents': contents}

    else:
        return {'type': 'text', 'text': '❓ 看不懂，輸入「說明」查看指令'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
