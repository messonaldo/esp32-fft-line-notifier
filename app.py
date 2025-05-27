from flask import Flask, request
import logging

# 建立 Flask App
app = Flask(__name__)

# 設定 logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.route('/', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()

        # 從 JSON 中取得 az 值
        az = data.get('az')

        if az is not None:
            logging.info(f"📡 接收到 az: {az}")
        else:
            logging.warning("⚠️ 沒有收到 az 值")

        return "OK", 200

    except Exception as e:
        logging.error(f"❌ 資料處理錯誤: {e}")
        return "Error", 500

# 測試首頁
@app.route('/', methods=['GET'])
def home():
    return "🔧 Render Server 正常運作中！"

