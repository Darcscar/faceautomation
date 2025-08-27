# app_render.py
import os
import json
import argparse
import logging
from flask import Flask, request
import requests

# ---------------------
# Flask App Setup
# ---------------------
app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ---------------------
# Tokens (replace with yours)
# ---------------------
PAGE_ACCESS_TOKEN = "EAHJTYAULctYBPcUwWzuDz7NrbC9gyFREogcTnAWoKuECFQTab4GcvnJWk0n0weADKloft2rFXVl6VvZA5tAH6wH9mZCZB2QUzaSznXBOvOZCBAqh2k2ut2ERo151Y18dSH9dt9Hgx7ETIThFtyLO9HmTiVHRbZAMCDdh18idUe6Uhm18WgIw4WuilbpJVQSpaqe3zEfzFtwZDZD"
VERIFY_TOKEN = "123darcscar"

# ---------------------
# Config
# ---------------------
FOODPANDA_URL = "https://www.foodpanda.ph/restaurant/locg/pedros-old-manila-rd"
MENU_URL = "https://darcscar.github.io/menu.pdf"
PHONE_NUMBER = "0424215968"
PAGE_NAME = "Pedro's Classic and Asian Cuisine"
FB_GRAPH = "https://graph.facebook.com/v19.0"

# ---------------------
# Helpers
# ---------------------
def call_send_api(psid, message_data):
    """Send message to user via Send API"""
    url = f"{FB_GRAPH}/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": psid},
        "messaging_type": "RESPONSE",
        "message": message_data,
    }
    try:
        r = requests.post(url, params=params, json=payload, timeout=20)
        r.raise_for_status()
        logger.debug("Message sent: %s", payload)
        return r.json()
    except requests.exceptions.RequestException as e:
        logger.error("Send API error: %s", e)
        return None

# ---------------------
# Menu Messages
# ---------------------
def send_vertical_menu(psid):
    msg = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {"title": "📋 View Menu", "subtitle": "See all dishes", "buttons": [{"type": "postback", "title": "Open Menu", "payload": "Q_VIEW_MENU"}]},
                    {"title": "🛵 Order on Foodpanda", "subtitle": "Order online", "buttons": [{"type": "web_url", "title": "Open Foodpanda", "url": FOODPANDA_URL}]},
                    {"title": "🍴 Advance Order", "subtitle": "Schedule in advance", "buttons": [{"type": "postback", "title": "Order Ahead", "payload": "Q_ADVANCE_ORDER"}]},
                    {"title": "📞 Contact Us", "subtitle": f"Reach us at {PHONE_NUMBER}", "buttons": [{"type": "postback", "title": "Call Us", "payload": "Q_CONTACT"}]},
                ]
            }
        }
    }
    return call_send_api(psid, msg)

# ---------------------
# Webhook
# ---------------------
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    logger.info("Webhook verification attempt: mode=%s, token=%s", mode, token)

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    app.logger.debug("Incoming: %s", json.dumps(data, indent=2))

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                psid = event.get("sender", {}).get("id")
                if not psid:
                    continue

                # Log the PSID of any new user
                app.logger.info(f"New user PSID: {psid}")

                # Handle messages
                if "message" in event:
                    msg = event["message"]
                    if msg.get("quick_reply"):
                        handle_payload(psid, msg["quick_reply"].get("payload"))
                    elif "text" in msg:
                        # Auto-respond to first message
                        send_vertical_menu(psid)
                        app.logger.info(f"Sent vertical menu to PSID {psid}")

                # Handle postbacks (like GET_STARTED)
                elif "postback" in event:
                    payload = event["postback"].get("payload")
                    app.logger.info(f"Received postback {payload} from PSID {psid}")
                    if payload == "GET_STARTED":
                        send_vertical_menu(psid)
                        app.logger.info(f"Sent vertical menu to PSID {psid}")
                    else:
                        handle_payload(psid, payload)
    return "EVENT_RECEIVED", 200

# ---------------------
# Run App
# ---------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", action="store_true", help="Run Messenger Profile setup and exit")
    args = parser.parse_args()

    PORT = int(os.getenv("PORT", 10000))  # Use Render-assigned port
    logger.info("Starting Flask app on port %s", PORT)

    if args.setup:
        print("Setup mode not implemented here.")
    else:
        app.run(host="0.0.0.0", port=PORT)
