from flask import Flask, request, jsonify
import logging
import threading
import time
import os
import numpy as np

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='🔍 %(asctime)s - %(message)s')

az_received_flag = {'received': False}
az_buffer = []  # 用來儲存 az 資料
FFT_SIZE = 256  # FFT 每批資料數量
SAMPLING_RATE = 10  # ESP32 傳送資料的頻率（Hz）

# 背景執行的線程：每秒顯示是否接收到資料
def print_empty_when_idle():
    while True:
        time.sleep(1)
        if not az_received_flag['received']:
            logging.info("Empty")
        else:
            az_received_flag['received'] = False

threading.Thread(target=print_empty_when_idle, daemon=True).start()

def perform_fft_and_log(az_data):
    # 轉成 numpy array 並移除直流分量（平均值）
    signal = np.array(az_data)
    signal = signal - np.mean(signal)

    # 執行 FFT
    fft_result = np.fft.fft(signal)
    freqs = np.fft.fftfreq(len(signal), d=1/SAMPLING_RATE)

    # 只取前半部（正頻率）
    magnitude = np.abs(fft_result[:len(signal)//2])
    freqs = freqs[:len(signal)//2]

    # 找主頻及其振幅
    peak_index = np.argmax(magnitude)
    peak_freq = freqs[peak_index]
    peak_amplitude = magnitude[peak_index]

    logging.info(f"📊 FFT 分析完成：主頻 = {peak_freq:.2f} Hz，振幅 = {peak_amplitude:.3f}")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        raw_data = request.data.decode('utf-8')
        logging.info(f"🟡 原始 request.data：{raw_data}")

        data = request.get_json(force=True)
        logging.info(f"🟢 解碼後 JSON：{data}")

        az = data.get('az') if data else None
        if az is not None:
            az_received_flag['received'] = True
            logging.info(f"✅ 接收到 az 資料：{az}")

            az_buffer.append(az)

            if len(az_buffer) >= FFT_SIZE:
                logging.info("🚀 資料累積完成，開始執行 FFT 分析...")
                perform_fft_and_log(az_buffer[:FFT_SIZE])
                del az_buffer[:FFT_SIZE]  # 清除已分析的資料

        else:
            logging.warning("⚠️ POST 中未包含 az 欄位")

    except Exception as e:
        logging.error(f"❌ 發生錯誤：{e}")

    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
