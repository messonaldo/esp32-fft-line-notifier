from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# 設定 Logging，顯示級別與格式
logging.basicConfig(level=logging.INFO, format="🔍 %(asctime)s - %(message)s")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    az = data.get('az')

    if az is not None:
        logging.info(f"接收到 az 資料：{az}")
    else:
        logging.warning("⚠️ 未收到有效的 az 資料")

    return jsonify({"status": "received"}), 200
