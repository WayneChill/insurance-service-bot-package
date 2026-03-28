"""
app.py ── 保險業務發展小幫手 LINE Bot
合併：產險助手 + 保服助手
Railway 部署：insurance-service-bot 專案
"""
import os
import json
import urllib.request
import urllib.error
from urllib.parse import unquote
from datetime import datetime
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    FlexSendMessage, PostbackEvent
)

# ── 讀取 config.txt（Railway 環境變數優先）────────────────
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

# ── 授權金鑰驗證 ──────────────────────────────────────────
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
        print("❌ 未提供授權金鑰")
        return False
    try:
        data = json.dumps({"key": key}).encode("utf-8")
        req  = urllib.request.Request(
            VERIFY_URL, data=data,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        if result.get("valid"):
            print(f"✅ 授權金鑰驗證成功（{result.get('user','')}，有效至 {result.get('expiry','')}）")
            return True
        print(f"❌ {result.get('message','金鑰驗證失敗')}")
        return False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"❌ 授權伺服器錯誤 HTTP {e.code}：{body[:200]}")
        return False
    except Exception as e:
        print(f"❌ 無法連線授權伺服器：{e}")
        return False

import sys
if not _verify_license():
    sys.exit(1)

# ── 初始化 ────────────────────────────────────────────────
from sheets import SheetsDB
from excel_reader import search_client
from flex_message import (
    build_client_card, build_cases_card,
    build_biz_list_card, build_help_message
)
from scheduler import start_scheduler

app      = Flask(__name__)
line_bot = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler  = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

# ── Lazy DB（第一次收到請求才連線，避免啟動卡死）──────────
_db = None

def get_db():
    global _db
    if _db is None:
        print("[DB] 初始化 SheetsDB...", flush=True)
        _db = SheetsDB()
        print("[DB] 完成，啟動排程", flush=True)
        start_scheduler(_db)
    return _db

# ── Webhook ───────────────────────────────────────────────
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body      = request.get_data(as_text=True)
    print("RECV", body[:80], flush=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return str(e), 500
    return "OK"

# ── 文字訊息處理 ──────────────────────────────────────────
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text  = event.message.text.strip()
    reply = _parse_command(text)
    if reply["type"] == "flex":
        line_bot.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text=reply["alt"], contents=reply["contents"])
        )
    else:
        line_bot.reply_message(
            event.reply_token,
            TextSendMessage(text=reply["text"])
        )

# ── Postback 處理 ─────────────────────────────────────────
@handler.add(PostbackEvent)
def handle_postback(event):
    data   = event.postback.data
    params = dict(p.split("=", 1) for p in data.split("&") if "=" in p)
    action = params.get("action", "")
    name   = unquote(params.get("name", ""))
    policy = unquote(params.get("policy", ""))

    if action in ("理賠", "契變", "保費變更"):
        case_id = get_db().add_case(name, action, policy)
        _reply_text(event, f"✅ 已開立案件 #{case_id}\n客戶：{name}\n項目：{action}\n\n輸入「進度 {name}」查看進度")
    elif action == "update":
        case_id = unquote(params.get("id", ""))
        status  = unquote(params.get("status", ""))
        get_db().update_case_status(case_id, status)
        _reply_text(event, f"✅ 案件 #{case_id} 已更新為「{status}」")
    elif action == "check_cases":
        cases    = get_db().get_cases(name)
        contents = build_cases_card(name, cases)
        _reply_flex(event, f"保服進度：{name}", contents)
    elif action in ("quoted", "delay", "delay7", "cancel", "done"):
        policy_id = unquote(params.get("id", ""))
        pname     = unquote(params.get("name", "保戶"))
        _LABELS = {
            "quoted": "已報價", "delay": "延後3天", "delay7": "延後7天",
            "cancel": "不續保", "done":  "續保完成",
        }
        _REPLIES = {
            "quoted": f"📋 {pname} 已報價，等待客戶確認",
            "delay":  f"⏰ {pname} 已延後，將在3天後提醒",
            "delay7": f"🔄 {pname} 已延後，將在7天後提醒",
            "cancel": f"❌ {pname} 已標記為不續保",
            "done":   f"✅ {pname} 續保完成，已記錄",
        }
        get_db().write_property_status(policy_id, pname, _LABELS[action])
        _reply_text(event, _REPLIES[action])
    else:
        _reply_text(event, "未知操作")


# ── 指令解析 ──────────────────────────────────────────────
def _parse_command(text: str) -> dict:
    parts = text.split()
    cmd   = parts[0] if parts else ""

    if cmd == "查詢" and len(parts) >= 2:
        name    = parts[1]
        clients = search_client(name)
        if not clients:
            return _t(f"❌ 找不到「{name}」的資料\n請確認姓名是否正確")
        cards    = get_db().get_cards(name)
        contents = build_client_card(clients, name, cards)
        return _f(f"客戶資料：{name}", contents)

    elif cmd == "進度" and len(parts) >= 2:
        name     = parts[1]
        cases    = get_db().get_cases(name)
        contents = build_cases_card(name, cases)
        return _f(f"保服進度：{name}", contents)

    elif cmd == "早報":
        try:
            from scheduler import _build_morning_report
            report = _build_morning_report(get_db())
            return _t(report)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return _t(f"❌ 早報錯誤：{e}")

    elif cmd == "保服":
        pending = get_db().get_all_pending_cases()
        if not pending:
            return _t("✅ 目前沒有待處理的保服案件")
        contents = build_cases_card("保服案件", pending)
        return _f("保服案件", contents)

    elif cmd == "待辦":
        try:
            import pandas as pd
            from excel_reader import download_excel
            urgent_list = []
            try:
                buf = download_excel("42004.xlsx")
                df  = pd.read_excel(buf, header=3)
                df.columns = df.columns.str.strip()
                df = df[df["保單號碼"].notna()]
                df = df[~df["保單號碼"].astype(str).str.contains("險種代號|附約")]
                def _roc(v):
                    try:
                        s = str(int(v)).zfill(7)
                        return pd.Timestamp(int(s[0:3])+1911, int(s[3:5]), int(s[5:7]))
                    except: return pd.NaT
                df["到期日"]   = df["保險迄日"].apply(_roc)
                today          = pd.Timestamp(datetime.today().date())
                df["剩餘天數"] = (df["到期日"] - today).dt.days
                urgent_df = df[
                    df["剩餘天數"].notna() &
                    df["剩餘天數"].between(0, 10) &
                    df["狀態"].astype(str).str.contains("正常")
                ]
                statuses = get_db().get_property_status()
                skip = {"續保完成", "不續保"}
                for _, row in urgent_df.iterrows():
                    pid = str(row["保單號碼"]).strip()
                    cur = statuses.get(pid, {}).get("status", "")
                    if cur not in skip:
                        urgent_list.append(f"▪️ {row['被保姓名']} 倒數{int(row['剩餘天數'])}天")
            except Exception:
                pass

            cases   = get_db().get_all_pending_cases()
            biz     = [r for r in get_db().get_biz_list() if r.get("階段") in ["已聯繫", "建議書"]]
            recruit = [r for r in get_db().get_recruit_list() if r.get("階段") in ["已聯繫", "約聊聊"]]

            lines = ["📌 今日待辦彙整", ""]
            lines.append(f"🚨 產險急件（{len(urgent_list)} 組）")
            lines += urgent_list[:5] if urgent_list else ["▪️ 無急件"]
            lines.append("")
            lines.append(f"📋 保服未完成（{len(cases)} 件）")
            lines += [f"▪️ {c.get('客戶姓名','')} {c.get('服務項目','')} [{c.get('狀態','')}]" for c in cases[:5]] if cases else ["▪️ 無待處理"]
            lines.append("")
            lines.append(f"💼 業務待跟進（{len(biz)} 組）")
            lines += [f"▪️ {b.get('姓名','')} [{b.get('階段','')}]" for b in biz[:5]] if biz else ["▪️ 無待跟進"]
            lines.append("")
            lines.append(f"👥 增員待跟進（{len(recruit)} 組）")
            lines += [f"▪️ {r.get('姓名','')} [{r.get('階段','')}]" for r in recruit[:5]] if recruit else ["▪️ 無待跟進"]

            return _t("\n".join(lines))
        except Exception as e:
            import traceback
            traceback.print_exc()
            return _t(f"❌ 待辦彙整錯誤：{e}")

    elif cmd in ("說明", "help", "?"):
        pending  = get_db().get_all_pending_cases()
        contents = build_help_message(pending)
        return _f("指令說明", contents)

    elif cmd == "產險":
        try:
            import pandas as pd
            from excel_reader import download_excel
            from flex_message import build_property_card
            buf = download_excel("42004.xlsx")
            df  = pd.read_excel(buf, header=3)
            df.columns = df.columns.str.strip()
            df = df[df["保單號碼"].notna()]
            df = df[~df["保單號碼"].astype(str).str.contains("險種代號|附約")]
            df["被保姓名"] = df["被保姓名"].astype(str).str.strip()
            df["行動電話"] = df["行動電話"].apply(lambda x: "0" + str(int(x)) if pd.notna(x) else "")
            def _roc(v):
                try:
                    s = str(int(v)).zfill(7)
                    return pd.Timestamp(int(s[0:3]) + 1911, int(s[3:5]), int(s[5:7]))
                except: return pd.NaT
            df["到期日"]   = df["保險迄日"].apply(_roc)
            today          = pd.Timestamp(datetime.today().date())
            df["剩餘天數"] = (df["到期日"] - today).dt.days
            urgent = df[
                df["剩餘天數"].notna() &
                df["剩餘天數"].between(0, 60) &
                df["狀態"].astype(str).str.contains("正常")
            ].copy().sort_values("剩餘天數")
            if urgent.empty:
                return _t("✅ 目前沒有60天內到期的產險")
            statuses = get_db().get_property_status()
            skip = {"續保完成", "不續保"}
            cards = []
            for _, row in urgent.iterrows():
                pid = str(row["保單號碼"]).strip()
                cur = statuses.get(pid, {}).get("status")
                if cur in skip:
                    continue
                cards.append(build_property_card(row, cur))
            if not cards:
                return _t("✅ 所有產險已處理完畢")
            contents = {"type": "carousel", "contents": cards[:10]}
            return _f(f"產險到期，共 {len(cards)} 筆", contents)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return _t(f"❌ 產險查詢錯誤：{e}")

    elif cmd == "壽險":
        try:
            from excel_reader import get_life_daily_detail
            from flex_message import build_life_detail_card
            detail   = get_life_daily_detail()
            contents = build_life_detail_card(detail)
            return _f("壽險提醒", contents)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return _t(f"❌ 壽險查詢錯誤：{e}")

    elif cmd == "業務":
        records  = get_db().get_biz_list()
        contents = build_biz_list_card(records, "💼 業務追蹤")
        return _f("業務追蹤", contents)

    elif cmd == "增員":
        records  = get_db().get_recruit_list()
        contents = build_biz_list_card(records, "👥 增員追蹤")
        return _f("增員追蹤", contents)

    elif cmd == "新增業務" and len(parts) >= 2:
        name  = parts[1]
        phone = parts[2] if len(parts) >= 3 else ""
        stage = parts[3] if len(parts) >= 4 else "已聯繫"
        rid   = get_db().add_biz(name, phone, stage)
        return _t(f"✅ 已新增業務追蹤 #{rid}\n姓名：{name}\n電話：{phone}\n階段：{stage}")

    elif cmd == "新增增員" and len(parts) >= 2:
        name  = parts[1]
        phone = parts[2] if len(parts) >= 3 else ""
        stage = parts[3] if len(parts) >= 4 else "已聯繫"
        rid   = get_db().add_recruit(name, phone, stage)
        return _t(f"✅ 已新增增員追蹤 #{rid}\n姓名：{name}\n電話：{phone}\n階段：{stage}")

    elif cmd == "更新業務" and len(parts) >= 3:
        rid, stage = parts[1], parts[2]
        ok = get_db().update_biz_stage(rid, stage)
        return _t(f"✅ 業務 {rid} 已更新為「{stage}」" if ok else f"❌ 找不到業務 {rid}")

    elif cmd == "更新增員" and len(parts) >= 3:
        rid, stage = parts[1], parts[2]
        ok = get_db().update_recruit_stage(rid, stage)
        return _t(f"✅ 增員 {rid} 已更新為「{stage}」" if ok else f"❌ 找不到增員 {rid}")

    elif cmd == "新增卡片" and len(parts) >= 5:
        c_name, c_bank, c_num, c_exp = parts[1], parts[2], parts[3], parts[4]
        c_policy = parts[5] if len(parts) >= 6 else ""
        get_db().add_card(c_name, c_bank, c_num, c_exp, c_policy)
        note = f"（指定保單：{c_policy}）" if c_policy else "（所有保單）"
        return _t(f"✅ 已新增信用卡\n姓名：{c_name}\n銀行：{c_bank}\n卡號：{c_num}\n效期：{c_exp}\n{note}")

    elif cmd == "刪除卡片" and len(parts) >= 4:
        c_name, c_bank, c_num = parts[1], parts[2], parts[3]
        ok = get_db().delete_card(c_name, c_bank, c_num)
        return _t(f"✅ 已刪除「{c_name}」{c_bank} {c_num} 的信用卡" if ok else "❌ 找不到該信用卡")

    else:
        return _t("❓ 看不懂指令，輸入「說明」查看所有指令")


# ── 工具 ──────────────────────────────────────────────────
def _t(text): return {"type": "text", "text": text}
def _f(alt, contents): return {"type": "flex", "alt": alt, "contents": contents}
def _reply_text(event, text): line_bot.reply_message(event.reply_token, TextSendMessage(text=text))
def _reply_flex(event, alt, contents): line_bot.reply_message(event.reply_token, FlexSendMessage(alt_text=alt, contents=contents))

@app.route("/", methods=["GET"])
def index(): return "保險業務發展小幫手 LINE Bot ✅"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET": return "OK", 200
    return callback()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
