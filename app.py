from flask import Flask, request
import datetime

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data or 'flag' not in data:
        return {"status": "error", "message": "No flag provided"}, 400

    flag = data['flag']
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] Received flag: {flag}")
    return {"status": "success"}
