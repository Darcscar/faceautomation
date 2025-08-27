# minimal_webhook.py
import os
import json
import logging
from flask import Flask, request

app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("FBWebhook")

# Your verify token
VERIFY_TOKEN = "123darcscar"

@app.route("/webhook", methods=["GET"])
def verify():
    """Webhook verification"""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    logger.info(f"Verification attempt: mode={mode}, token={token}")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    """Log everything Facebook sends"""
    data = request.get_json()
    logger.info("Webhook received:\n%s", json.dumps(data, indent=2))
    # Also print to stdout to ensure Render logs catch it
    print("Webhook received:", json.dumps(data, indent=2))
    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 10000))
    logger.info(f"Starting minimal webhook on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)

