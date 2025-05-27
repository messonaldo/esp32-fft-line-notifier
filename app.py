from flask import Flask, request, jsonify
import numpy as np
import logging
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

LINE_TOKEN = "GxKQCTE6XpBYDN9Z/WtWQVAR3WEkAwR/5eGIN2MXlfiXohV3BjxTYalySy2HBN7rLmyaTtMj/ONe+FUCZa3etR5aXqroXqGxyQUkPZ+9Kfwj7X/++HrngGIkT7/bWcKRQAionzH0QC/YByoEmW9rDgdB04t89/1O/w1cDnyilFU="

def send_line_notify(message):
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    payload = {'message': message}
    response = requests.post(url, headers=headers, data=payload)
    logging.info(f"LINE Notify 發送狀態碼: {response.status_code}")
    return response.status_code

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        az = data.get('az', [])
        if not az:
            logging.warning("未接收到 az 資料")
            return jsonify({"status": "error", "message": "No az data received"}), 400

        # FFT 分析
        az_np = np.array(az)
        fft = np.fft.fft(az_np)
        freq = np.fft.fftfreq(len(az_np), d=1/1000)  # 假設取樣率為 1000Hz

        amplitude = np.abs(fft)
        idx = np.argmax(amplitude[:len(amplitude)//2])
        main_freq = freq[idx]
        main_amp = amplitude[idx]

        message = f"主頻率：{main_freq:.2f} Hz\n, 振幅：{main_amp:.2f}"
        logging.info(f"送出訊息: {message}")
        send_line_notify(message)

        return jsonify({"status": "success", "main_freq": main_freq, "amplitude": main_amp})
    except Exception as e:
        logging.exception("發生例外錯誤")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
