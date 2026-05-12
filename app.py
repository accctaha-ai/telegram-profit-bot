from flask import Flask, request
import requests
import os
import threading

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WAIT_SECONDS = int(os.getenv("WAIT_SECONDS", "5"))

buffer = {}
timers = {}

def send_telegram(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
        timeout=10
    )

def flush(login):
    trades = buffer.pop(login, [])
    timers.pop(login, None)

    if not trades:
        return

    first = trades[0]
    total_profit = sum(float(t["profit"]) for t in trades)

    text = f"""🚨 High Profit Alert 🚨

Client: {first["client"]}
Account: {login}
Balance: {first["balance"]}
Total Profit: {total_profit:.2f}
Positions Count: {len(trades)}
"""

    send_telegram(text)

@app.route("/")
def home():
    return "running"

@app.route("/trade")
def trade():
    login = request.args.get("login", "")
    client = request.args.get("client", "")
    balance = request.args.get("balance", "")
    profit = request.args.get("profit", "0")

    if not login:
        return {"ok": False, "error": "missing login"}, 400

    buffer.setdefault(login, []).append({
        "client": client,
        "balance": balance,
        "profit": profit
    })

    if login in timers:
        timers[login].cancel()

    timer = threading.Timer(WAIT_SECONDS, flush, args=[login])
    timers[login] = timer
    timer.start()

    return {"ok": True, "queued": len(buffer[login])}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
