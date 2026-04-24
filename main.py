import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram(message):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
    )

def format_signal(signal):
    signal = signal.strip()
    if signal.upper() == "BUY":
        return "🟢 BUY"
    elif signal.upper() == "SELL":
        return "🔴 SELL"
    else:
        return f"📌 {signal}"

@app.route("/")
def home():
    return "Bot is running!", 200

@app.route("/webhook/chartink", methods=["POST"])
def chartink_webhook():
    data = request.get_json(force=True)

    scan_name = data.get("scan_name", "Alert")
    stocks = data.get("stocks", "").split(",")
    prices = data.get("trigger_prices", "").split(",")
    triggered_at = data.get("triggered_at", "")

    now = datetime.now()
    date_str = now.strftime("%a %d %b")

    lines = []
    for stock, price in zip(stocks, prices):
        try:
            formatted_price = f"{float(price.strip()):,.2f}"
        except:
            formatted_price = price.strip()
        lines.append(f"📈 `{stock.strip():<12}` ₹{formatted_price}")

    message = (
        f"🚨 *ALERT TRIGGERED* 🚨\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📌 {scan_name}\n"
        f"📌 NSE  •  Realtime\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        + "\n".join(lines) +
        f"\n━━━━━━━━━━━━━━━━━━━\n"
        f"📌 Scan Triggered\n"
        f"🕐 {triggered_at}  •  {date_str}"
    )

    send_telegram(message)
    return jsonify({"status": "ok"})

@app.route("/webhook/tradingview", methods=["POST"])
def tradingview_webhook():
    data = request.get_json(force=True)

    indicator = data.get("indicator", "TradingView Alert")
    symbol = data.get("symbol", "")
    exchange = data.get("exchange", "")
    price = data.get("price", "")
    interval = data.get("interval", "")
    signal = data.get("signal", "Scan Triggered")
    time_str = data.get("time", "")

    try:
        formatted_price = f"{float(price):,.2f}"
    except:
        formatted_price = price

    now = datetime.now()
    date_str = now.strftime("%a %d %b")

    message = (
        f"🚨 *ALERT TRIGGERED* 🚨\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📌 {indicator}\n"
        f"📌 {exchange}  •  {interval}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📈 `{symbol:<12}` ₹{formatted_price}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"{format_signal(signal)}\n"
        f"🕐 {time_str}  •  {date_str}"
    )

    send_telegram(message)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
