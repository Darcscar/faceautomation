# app.py
# Facebook Messenger bot in Python (Flask) with Vertical Menu (Generic Template)

import os
import json
import argparse
from flask import Flask, request
import requests

app = Flask(__name__)

# ---------------------
# Tokens (replace with yours)
# ---------------------
PAGE_ACCESS_TOKEN = "EAAPUTGXVbPcBPTSItwjWd91fMOjUG55JrSlgfXtUiNcVpnnA4c0olY70GFRjrPKL9L2vY4R0C0mXvdeXg5V361ZC2fVE48HlRoNvpTek7NPc3VFH4nrpxQWfDejoQkXT5L7DtJeuqdyywrlooerZAshU0EvkXdaORLdjYYCUumS4WIgZA48euntgEYgYbYLh6WkO2LrZB7nEE23mgRI8bgZDZD"
VERIFY_TOKEN = "123darcscar"

# ---------------------
# Config
# ---------------------
FOODPANDA_URL = "https://www.foodpanda.ph/restaurant/locg/pedros-old-manila-rd"
MENU_URL = "https://darcscar.github.io/menu.pdf"   # <--- put your menu photo/PDF URL here
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
    r = requests.post(url, params=params, json=payload, timeout=20)
    if r.status_code >= 300:
        app.logger.error("Send API error %s: %s", r.status_code, r.text)
    return r.json() if r.text else {}

# ---------------------
# Vertical Menu
# ---------------------

def send_vertical_menu(psid):
    """Sends a vertical-style menu using Messenger Generic Template"""
    msg = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": "📋 View Menu",
                        "subtitle": "See all our dishes and prices",
                        "buttons": [
                            {"type": "postback", "title": "Open Menu", "payload": "Q_VIEW_MENU"}
                        ],
                    },
                    {
                        "title": "🛵 Order on Foodpanda",
                        "subtitle": "Order online via Foodpanda",
                        "buttons": [
                            {"type": "web_url", "title": "Open Foodpanda", "url": FOODPANDA_URL}
                        ],
                    },
                    {
                        "title": "🍴 Advance Order",
                        "subtitle": "Schedule your order in advance",
                        "buttons": [
                            {"type": "postback", "title": "Order Ahead", "payload": "Q_ADVANCE_ORDER"}
                        ],
                    },
                    {
                        "title": "📞 Contact Us",
                        "subtitle": f"Reach us at {PHONE_NUMBER}",
                        "buttons": [
                            {"type": "postback", "title": "Call Us", "payload": "Q_CONTACT"}
                        ],
                    },
                ]
            }
        }
    }
    return call_send_api(psid, msg)

# ---------------------
# Other Messages
# ---------------------

def send_foodpanda_buttons(psid):
    msg = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "button",
                "text": "Order through Foodpanda here:",
                "buttons": [
                    {
                        "type": "web_url",
                        "url": "https://tinyurl.com/bdhczune",
                        "title": "🛵 Open Foodpanda",
                        "webview_height_ratio": "tall",
                    }
                ],
            },
        }
    }
    return call_send_api(psid, msg)

def send_advance_order_info(psid):
    text = (
        "✅ Yes, we accept advance orders!\n\n"
        "• For Foodpanda: schedule inside the Foodpanda app.\n"
        "• For dine-in/pickup: reply with your order and preferred time here.\n\n"
        "We’ll have it ready fresh when you arrive. 🕑✨"
    )
    call_send_api(psid, {"text": text})
    return send_vertical_menu(psid)

def send_contact_info(psid):
    text = f"📞 You can reach us at {PHONE_NUMBER}.\nOr just reply here and a staff member will assist you."
    call_send_api(psid, {"text": text})
    return send_vertical_menu(psid)

def send_menu(psid):
    msg = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "button",
                "text": "📋 Here’s our full menu:",
                "buttons": [
                    {
                        "type": "web_url",
                        "url": "https://imgur.com/a/byqpSBq",
                        "title": "📖 Open Menu",
                        "webview_height_ratio": "full"
                    }
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

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    app.logger.debug("Incoming: %s", json.dumps(data))

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                psid = event.get("sender", {}).get("id")
                if "message" in event:
                    msg = event["message"]
                    if msg.get("quick_reply"):
                        handle_payload(psid, msg["quick_reply"].get("payload"))
                    elif "text" in msg:
                        send_vertical_menu(psid)
                elif "postback" in event:
                    payload = event["postback"].get("payload")
                    if payload == "GET_STARTED":
                        send_vertical_menu(psid)
                    else:
                        handle_payload(psid, payload)
    return "EVENT_RECEIVED", 200

# ---------------------
# Payload Routing
# ---------------------

def handle_payload(psid, payload):
    if not payload:
        return send_vertical_menu(psid)
    if payload in {"Q_VIEW_MENU", "P_VIEW_MENU"}:
        return send_menu(psid)
    if payload in {"Q_FOODPANDA", "P_FOODPANDA"}:
        return send_foodpanda_buttons(psid)
    if payload in {"Q_ADVANCE_ORDER", "P_ADVANCE_ORDER"}:
        return send_advance_order_info(psid)
    if payload in {"Q_CONTACT", "P_CONTACT"}:
        return send_contact_info(psid)
    return send_vertical_menu(psid)

# ---------------------
# Profile Setup
# ---------------------

def setup_profile():
    headers = {"Content-Type": "application/json"}
    params = {"access_token": PAGE_ACCESS_TOKEN}

    # Get Started button
    payload = {"get_started": {"payload": "GET_STARTED"}}
    r = requests.post(f"{FB_GRAPH}/me/messenger_profile", params=params, headers=headers, json=payload, timeout=20)
    print("Get Started:", r.status_code, r.text)

    # Persistent Menu
    menu = {
        "persistent_menu": [
            {
                "locale": "default",
                "composer_input_disabled": False,
                "call_to_actions": [
                    {"type": "postback", "title": "📋 View Menu", "payload": "P_VIEW_MENU"},
                    {"type": "web_url", "title": "🛵 Order on Foodpanda", "url": FOODPANDA_URL, "webview_height_ratio": "tall"},
                    {"type": "postback", "title": "🍴 Advance Order", "payload": "P_ADVANCE_ORDER"},
                    {"type": "postback", "title": "📞 Contact Us", "payload": "P_CONTACT"},
                ],
            }
        ]
    }
    r2 = requests.post(f"{FB_GRAPH}/me/messenger_profile", params=params, headers=headers, json=menu, timeout=20)
    print("Persistent Menu:", r2.status_code, r2.text)

# ---------------------
# Run App
# ---------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", action="store_true", help="Run Messenger Profile setup and exit")
    parser.add_argument("--port", default=os.getenv("PORT", "8080"))
    args = parser.parse_args()

    if args.setup:
        setup_profile()
    else:
        app.run(host="0.0.0.0", port=int(args.port))
