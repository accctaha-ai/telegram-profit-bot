from flask import Flask, request
import requests
import os
import threading
import re

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WAIT_SECONDS = int(os.getenv("WAIT_SECONDS", "5"))

buffer = {}
timers = {}

def to_number(value):
    if value is None:
        return 0.0
    value = str(value).replace(",", "").strip()
    value = re.sub(r"[^0-9.\-]", "", value)
    try:
        return float(value)
    except:
        return 0.0

def send_telegram(text):
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
        timeout=10
    )
    print("Telegram response:", r.status_code, r.text)

def flush(login):
    try:
        trades = buffer.pop(login, [])
        timers.pop(login, None)

        if not trades:
            return

        first = trades[0]
        total_profit = sum(to_number(t.get("profit")) for t in trades)

        text = f"""🚨 High Profit Alert 🚨

Client: {first.get("client", "")}
Account: {login}
Balance: {first.get("balance", "")}
Total Profit: {total_profit:.2f}
Positions Count: {len(trades)}
"""

        send_telegram(text)

    except Exception as e:
        print("FLUSH ERROR:", str(e))

@app.route("/")
def home():
    return "running"

@app.route("/trade")
def trade():
    try:
        login = request.args.get("login", "").strip()
        client = request.args.get("client", "")
        balance = request.args.get("balance", "")
        profit = request.args.get("profit", "0")
        symbol = request.args.get("symbol", "")

        print("RECEIVED:", dict(request.args))

        if not login:
            return {"ok": False, "error": "missing login"}, 400

        buffer.setdefault(login, []).append({
            "client": client,
            "balance": balance,
            "profit": profit,
            "symbol": symbol
        })

        if login in timers:
            timers[login].cancel()

        timer = threading.Timer(WAIT_SECONDS, flush, args=[login])
        timers[login] = timer
        timer.start()

        return {"ok": True, "queued": len(buffer[login])}

    except Exception as e:
        print("TRADE ERROR:", str(e))
        return {"ok": False, "error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
