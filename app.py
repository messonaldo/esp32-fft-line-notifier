from flask import Flask, request, jsonify
import logging
import threading
import time

app = Flask(__name__)

# 設定 logging 輸出格式
logging.basicConfig(level=logging.INFO, format='🔍 %(asctime)s - %(message)s')

# 控制是否接收到 az
az_received_flag = {'received': False}

def print_empty_when_idle():
    while True:
        time.sleep(1)
        if not az_received_flag['received']:
            logging.info("Empty")
        else:
            az_received_flag['received'] = False  # 重置 flag

# 啟動背景 thread 印出 Empty
threading.Thread(target=print_empty_when_idle, daemon=True).start()

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)  # 強制解析 JSON
        az = data.get('az')

        if az is not None:
            az_received_flag['received'] = True
            logging.info(f"接收到 az 資料：{az}")
        else:
            logging.warning("⚠️ POST 中未包含 az 資料")
    except Exception as e:
        logging.error(f"❌ 發生錯誤：{e}")

    return jsonify({"status": "received"}), 200
