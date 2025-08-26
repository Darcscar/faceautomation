from flask import Flask, request, Response

app = Flask(__name__)

VERIFY_TOKEN = "123darcscar"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode", "")
        token = request.args.get("hub.verify_token", "")
        challenge = request.args.get("hub.challenge", "")

        print("👉 Incoming verification request:")
        print("mode:", repr(mode))
        print("token from facebook:", repr(token))
        print("token from code:", repr(VERIFY_TOKEN))
        print("challenge:", repr(challenge))

        if mode.strip() == "subscribe" and token.strip() == VERIFY_TOKEN:
            print("✅ Verification success!")
            return Response(challenge, status=200, mimetype="text/plain")
        else:
            print("❌ Verification failed!")
            return Response("Forbidden", status=403)

    if request.method == "POST":
        data = request.get_json()
        print("📩 Incoming webhook event:", data)
        return Response("EVENT_RECEIVED", status=200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
