from flask import Flask, request, jsonify
import logging
import threading
import time
import numpy as np
from scipy.fft import rfft, rfftfreq

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='🔍 %(asctime)s - %(message)s')

az_buffer = []
time_buffer = []
BUFFER_SIZE = 256  # 或可改 128

def compute_fft():
    global az_buffer, time_buffer
    if len(az_buffer) < BUFFER_SIZE:
        return

    # 複製資料以避免干擾
    az_data = np.array(az_buffer[:BUFFER_SIZE])
    time_data = np.array(time_buffer[:BUFFER_SIZE])
    az_buffer = az_buffer[BUFFER_SIZE:]
    time_buffer = time_buffer[BUFFER_SIZE:]

    # 計算時間差與採樣頻率 (Hz)
    time_diff_ms = time_data[-1] - time_data[0]
    duration_sec = time_diff_ms / 1000.0
    if duration_sec == 0:
        return

    fs = BUFFER_SIZE / duration_sec  # 採樣頻率
    yf = np.abs(rfft(az_data))
    xf = rfftfreq(BUFFER_SIZE, 1 / fs)

    idx = np.argmax(yf)
    dominant_freq = xf[idx]
    amplitude = yf[idx]

    logging.info(f"📈 FFT 主頻: {dominant_freq:.2f} Hz, 振幅: {amplitude:.3f}")
    logging.info(f"⏱ 資料時間範圍: {time_data[0]} ~ {time_data[-1]} ms")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        az = data.get('az')
        timestamp = data.get('timestamp')

        if az is not None and timestamp is not None:
            az_buffer.append(az)
            time_buffer.append(timestamp)
            logging.info(f"✅ 接收 az: {az:.3f}, timestamp: {timestamp}")
            compute_fft()
        else:
            logging.warning("⚠️ 資料缺少 az 或 timestamp")

    except Exception as e:
        logging.error(f"❌ 錯誤: {e}")

    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
