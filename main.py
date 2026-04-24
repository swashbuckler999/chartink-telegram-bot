import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

@app.route("/")
def home():
    return "Bot is running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    scan_name = data.get("scan_name", "Alert")
    stocks = data.get("stocks", "").split(",")
    prices = data.get("trigger_prices", "").split(",")
    triggered_at = data.get("triggered_at", "")

    # Format date like "Mon 24 Apr"
    now = datetime.now()
    date_str = now.strftime("%a %d %b")

    # Pair each stock with its price
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
        f"📌 Scan  : {scan_name}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        + "\n".join(lines) +
        f"\n━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 {triggered_at}  •  {date_str}"
    )

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
    )
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
