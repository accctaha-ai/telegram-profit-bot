from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

@app.route("/")
def home():
    return "running"

@app.route("/trade")
def trade():
    login = request.args.get("login")
    client = request.args.get("client")
    balance = request.args.get("balance")
    profit = request.args.get("profit")
    symbol = request.args.get("symbol")

    text = f"""🚨 High Profit Alert 🚨

Client: {client}
Account: {login}
Balance: {balance}
Profit: {profit}
Symbol: {symbol}
"""

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    )

    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
