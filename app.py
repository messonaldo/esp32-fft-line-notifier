from flask import Flask, request, jsonify
import logging
import threading
import time
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='🔍 %(asctime)s - %(message)s')

az_received_flag = {'received': False}

def print_empty_when_idle():
    while True:
        time.sleep(1)
        if not az_received_flag['received']:
            logging.info("Empty")
        else:
            az_received_flag['received'] = False

threading.Thread(target=print_empty_when_idle, daemon=True).start()

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        az = data.get('az')
        logging.info(f"原始資料：{request.data}")

        if az is not None:
            az_received_flag['received'] = True
            logging.info(f"接收到 az 資料：{az}")
        else:
            logging.warning("⚠️ POST 中未包含 az 資料")
    except Exception as e:
        logging.error(f"❌ 發生錯誤：{e}")

    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
