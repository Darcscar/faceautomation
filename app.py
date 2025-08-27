import os
import json
import logging
from flask import Flask, request, Response
import requests

# ---------------------
# Flask App Setup
# ---------------------
app = Flask(__name__)

# ---------------------
# Logging
# ---------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------
# Facebook Tokens
# ---------------------
PAGE_ACCESS_TOKEN = "EAHJTYAULctYBPcUwWzuDz7NrbC9gyFREogcTnAWoKuECFQTab4GcvnJWk0n0weADKloft2rFXVl6VvZA5tAH6wH9mZCZB2QUzaSznXBOvOZCBAqh2k2ut2ERo151Y18dSH9dt9Hgx7ETIThFtyLO9HmTiVHRbZAMCDdh18idUe6Uhm18WgIw4WuilbpJVQSpaqe3zEfzFtwZDZD"
VERIFY_TOKEN = "123darcscar"
FB_GRAPH = "https://graph.facebook.com/v19.0"

# ---------------------
# Helpers
# ---------------------
def send_text_message(psid, message):
    """Send a simple text message to the user"""
    url = f"{FB_GRAPH}/me/messages"
    payload = {
        "recipient": {"id": psid},
        "messaging_type": "RESPONSE",
        "message": {"text": message},
    }
    params = {"access_token": PAGE_ACCESS_TOKEN}
    try:
        r = requests.post(url, json=payload, params=params, timeout=20)
        r.raise_for_status()
        logger.info(f"✅ Sent message to {psid}: {message}")
        return r.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Send API error: {e}")
        return None

# ---------------------
# Webhook Verification
# ---------------------
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode", "")
    token = request.args.get("hub.verify_token", "")
    challenge = request.args.get("hub.challenge", "")

    logger.info(f"Webhook verification attempt: mode={mode}, token={token}")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("✅ Verification successful")
        return Response(challenge, status=200, mimetype="text/plain")
    else:
        logger.warning("❌ Verification failed")
        return Response("Forbidden", status=403)

# ---------------------
# Webhook POST
# ---------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    logger.info(f"📩 Incoming webhook: {json.dumps(data, indent=2)}")

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                sender_id = event.get("sender", {}).get("id")
                if not sender_id:
                    continue

                # Log the PSID
                logger.info(f"👤 Sender PSID: {sender_id}")

                # Handle messages
                if "message" in event and "text" in event["message"]:
                    text = event["message"]["text"]
                    logger.info(f"💬 Received message: {text}")
                    send_text_message(sender_id, f"You said: {text}")

                # Handle postbacks
                elif "postback" in event:
                    payload = event["postback"].get("payload")
                    logger.info(f"🔘 Received postback: {payload}")
                    send_text_message(sender_id, f"Postback received: {payload}")

    return Response("EVENT_RECEIVED", status=200)

# ---------------------
# Run Flask App
# ---------------------
if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 10000))
    logger.info(f"🚀 Starting Flask app on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
