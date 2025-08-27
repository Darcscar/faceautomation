import os
import json
import logging
from flask import Flask, request, Response
import requests

# ---------------------
# Flask Setup
# ---------------------
app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------
# Facebook Tokens
# ---------------------
PAGE_ACCESS_TOKEN = "EAHJTYAULctYBPcUwWzuDz7NrbC9gyFREogcTnAWoKuECFQTab4GcvnJWk0n0weADKloft2rFXVl6VvZA5tAH6wH9mZCZB2QUzaSznXBOvOZCBAqh2k2ut2ERo151Y18dSH9dt9Hgx7ETIThFtyLO9HmTiVHRbZAMCDdh18idUe6Uhm18WgIw4WuilbpJVQSpaqe3zEfzFtwZDZD"
VERIFY_TOKEN = "123darcscar"
FB_GRAPH = "https://graph.facebook.com/v19.0"

# ---------------------
# Config
# ---------------------
FOODPANDA_URL = "https://www.foodpanda.ph/restaurant/locg/pedros-old-manila-rd"
PHONE_NUMBER = "0424215968"

# ---------------------
# Helpers
# ---------------------
def send_vertical_menu(psid):
    """Send vertical menu using Generic Template"""
    msg = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": "📋 View Menu",
                        "subtitle": "See all our dishes and prices",
                        "buttons": [{"type": "postback", "title": "Open Menu", "payload": "Q_VIEW_MENU"}]
                    },
                    {
                        "title": "🛵 Order on Foodpanda",
                        "subtitle": "Order online via Foodpanda",
                        "buttons": [{"type": "web_url", "title": "Open Foodpanda", "url": FOODPANDA_URL}]
                    },
                    {
                        "title": "🍴 Advance Order",
                        "subtitle": "Schedule your order in advance",
                        "buttons": [{"type": "postback", "title": "Order Ahead", "payload": "Q_ADVANCE_ORDER"}]
                    },
                    {
                        "title": "📞 Contact Us",
                        "subtitle": f"Reach us at {PHONE_NUMBER}",
                        "buttons": [{"type": "postback", "title": "Call Us", "payload": "Q_CONTACT"}]
                    },
                ]
            }
        }
    }
    return call_send_api(psid, msg)

def call_send_api(psid, message_data):
    """Send message via Messenger Send API"""
    url = f"{FB_GRAPH}/me/messages"
    payload = {
        "recipient": {"id": psid},
        "messaging_type": "RESPONSE",
        "message": message_data
    }
    params = {"access_token": PAGE_ACCESS_TOKEN}
    try:
        r = requests.post(url, json=payload, params=params, timeout=20)
        r.raise_for_status()
        logger.info(f"✅ Sent vertical menu to PSID {psid}")
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
                psid = event.get("sender", {}).get("id")
                if not psid:
                    continue

                logger.info(f"👤 Sender PSID: {psid}")

                # Send vertical menu for any message or GET_STARTED postback
                if "message" in event or ("postback" in event and event["postback"].get("payload") == "GET_STARTED"):
                    send_vertical_menu(psid)

    return Response("EVENT_RECEIVED", status=200)

# ---------------------
# Run Flask App
# ---------------------
if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 10000))
    logger.info(f"🚀 Starting Flask app on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
