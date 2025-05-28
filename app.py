from flask import Flask, request, jsonify
import logging
import numpy as np
from scipy.fft import rfft, rfftfreq

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

az_buffer = []
time_buffer = []
BUFFER_SIZE = 256

def compute_fft():
    global az_buffer, time_buffer
    if len(az_buffer) < BUFFER_SIZE:
        return

    az_data = np.array(az_buffer[:BUFFER_SIZE])
    time_data = np.array(time_buffer[:BUFFER_SIZE])
    az_buffer.clear()
    time_buffer.clear()

    time_diff_ms = time_data[-1] - time_data[0]
    if time_diff_ms == 0:
        return

    duration_sec = time_diff_ms / 1000.0
    fs = BUFFER_SIZE / duration_sec

    yf = np.abs(rfft(az_data))
    xf = rfftfreq(BUFFER_SIZE, 1 / fs)

    idx = np.argmax(yf)
    dominant_freq = xf[idx]
    amplitude = yf[idx]

    logging.info(f"📈 FFT 主頻: {dominant_freq:.2f} Hz, 振幅: {amplitude:.3f}")
    logging.info(f"⏱ 資料時間範圍: {time_data[0]} ~ {time_data[-1]} ms")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and 'az' in data and 'timestamp' in data:
        az = float(data['az'])
        timestamp = int(data['timestamp'])
        az_buffer.append(az)
        time_buffer.append(timestamp)
        logging.info(f"✅ 接收 az: {az:.3f}, timestamp: {timestamp}")
        compute_fft()
        return jsonify({'status': 'ok'}), 200
    else:
        logging.warning("⚠️ 無效資料格式")
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
