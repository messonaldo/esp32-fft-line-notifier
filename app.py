from flask import Flask, request, jsonify
import numpy as np
import requests
import os

app = Flask(__name__)

LINE_TOKEN = "GxKQCTE6XpBYDN9Z/WtWQVAR3WEkAwR/5eGIN2MXlfiXohV3BjxTYalySy2HBN7rLmyaTtMj/ONe+FUCZa3etR5aXqroXqGxyQUkPZ+9Kfwj7X/++HrngGIkT7/bWcKRQAionzH0QC/YByoEmW9rDgdB04t89/1O/w1cDnyilFU="
USER_ID = "Ue428e46d6380ba97aaca7b234375bf3c"

# 儲存最近的 az 資料
az_data = []

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    az = data.get('az')
    if az is None:
        return jsonify({'status': 'error', 'message': 'No az value provided'}), 400

    az_data.append(az)
    if len(az_data) > 100:
        az_data.pop(0)

    # 當資料量足夠時進行 FFT 分析
    if len(az_data) == 100:
        y = np.array(az_data)
        y = y - np.mean(y)
        N = len(y)
        fs = 100  # 假設取樣頻率為 100 Hz
        f = np.fft.rfftfreq(N, d=1/fs)
        Y = np.fft.rfft(y)
        amplitude = np.abs(Y)

        peak_idx = np.argmax(amplitude)
        peak_freq = f[peak_idx]
        peak_amp = amplitude[peak_idx]

        if peak_freq == 100 and peak_amp >= 5:
            send_line_message(f"偵測到振動頻率為 {peak_freq} Hz，振幅為 {peak_amp:.2f}")

    return jsonify({'status': 'success'}), 200

def send_line_message(message):
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=data)
    return response.status_code

if __name__ == '__main__':
    app.run()
