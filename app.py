from flask import Flask, request, jsonify
import numpy as np
import logging
import requests

app = Flask(__name__)

# ✅ 設定 logging 格式與等級
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 🔐 LINE Notify 權杖
LINE_TOKEN = "GxKQCTE6XpBYDN9Z/WtWQVAR3WEkAwR/5eGIN2MXlfiXohV3BjxTYalySy2HBN7rLmyaTtMj/ONe+FUCZa3etR5aXqroXqGxyQUkPZ+9Kfwj7X/++HrngGIkT7/bWcKRQAionzH0QC/YByoEmW9rDgdB04t89/1O/w1cDnyilFU="

def send_line_notify(message):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    payload = {"message": message}
    r = requests.post(url, headers=headers, data=payload)
    return r.status_code

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # ✅ 原始 print：保留
    print("📥 Received data:", data)

    # ✅ Logging 輸出
    logging.info("📥 Received data: %s", data)

    # 只處理 az 資料
    az_values = data.get('az', [])
    if not az_values:
        print("⚠️ No az data received.")
        logging.warning("⚠️ No az data received.")
        return jsonify({'status': 'no az data'}), 400

    az_array = np.array(az_values)

    # ✅ FFT 分析
    fft_result = np.fft.fft(az_array)
    fft_magnitude = np.abs(fft_result)
    freq = np.fft.fftfreq(len(az_array), d=1/1000)  # 假設 1kHz 取樣率

    # ✅ 主頻分析
    peak_index = np.argmax(fft_magnitude[1:]) + 1
    peak_freq = abs(freq[peak_index])
    peak_amplitude = fft_magnitude[peak_index]

    print(f"📊 Peak frequency: {peak_freq:.2f} Hz, Amplitude: {peak_amplitude:.2f}")
    logging.info("📊 Peak frequency: %.2f Hz, Amplitude: %.2f", peak_freq, peak_amplitude)

    # ✅ 判斷是否觸發事件
    if int(round(peak_freq)) == 100 and peak_amplitude >= 5:
        message = f"🚨 偵測到異常震動！頻率：{peak_freq:.2f} Hz，振幅：{peak_amplitude:.2f}"
        print("🔔 Sending LINE Notify:", message)
        logging.info("🔔 Sending LINE Notify: %s", message)

        response_code = send_line_notify(message)
        return jsonify({'status': 'alert sent', 'code': response_code}), 200
    else:
        print("✅ 正常狀態，未觸發警報。")
        logging.info("✅ Normal condition. No alert triggered.")
        return jsonify({'status': 'normal'}), 200

@app.route('/')
def home():
    return "LINE Notify Vibration Monitoring Server is running."
