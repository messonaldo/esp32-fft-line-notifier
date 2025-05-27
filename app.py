from flask import Flask, request, jsonify
import logging
import threading
import time

app = Flask(__name__)

# 設定 logging 格式與等級
logging.basicConfig(level=logging.INFO, format='🔍 %(asctime)s - %(message)s')

# 是否接收到 az 的旗標
az_received_flag = {'received': False}

# 背景 Thread：每秒檢查是否接收到 az，否則印出 Empty
def print_empty_when_idle():
    while True:
        time.sleep(1)
        if not az_received_flag['received']:
            logging.info("Empty")
        else:
            az_received_flag['received'] = False  # 重設旗標

# 啟動背景執行緒
threading.Thread(target=print_empty_when_idle, daemon=True).start()

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # 印出原始 payload，方便 debug
        logging.info(f"原始資料：{request.data}")

        # 檢查 Content-Type 並強制解析 JSON
        if request.is_json:
            data = request.get_json(force=True)
            az = data.get('az')

            if az is not None:
                az_received_flag['received'] = True
                logging.info(f"接收到 az 資料：{az}")
            else:
                logging.warning("⚠️ POST 中未包含 az 資料")
        else:
            logging.warning(f"⚠️ Content-Type 不是 JSON：{request.content_type}")

    except Exception as e:
        logging.error(f"❌ 發生錯誤：{e}")

    return jsonify({"status": "received"}), 200
