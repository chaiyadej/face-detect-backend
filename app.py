# app.py (Backend)
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import base64
import re

app = Flask(__name__)
CORS(app)

# ดึง Token จาก Environment Variable ที่คุณเพิ่งตั้ง
LINE_NOTIFY_TOKEN = os.environ.get('LINE_NOTIFY_TOKEN')
LINE_API_URL = 'https://notify-api.line.me/api/notify'

@app.route('/detect-action', methods=['POST'])
def detect_action():
    try:
        data = request.json
        face_count = data.get('face_count', 0)
        image_base64 = data.get('image', '')

        if not LINE_NOTIFY_TOKEN:
            return jsonify({'status': 'error', 'message': 'Token not found on Server'}), 500

        # --- ส่วนสำคัญ: แปลงภาพให้ชัวร์ ---
        # 1. ถ้ามี header "data:image/jpeg;base64," ให้ตัดทิ้ง
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        
        # 2. แปลงกลับเป็นไฟล์ภาพ
        image_bytes = base64.b64decode(image_base64)
        
        # 3. เตรียมส่งเข้า LINE
        headers = {'Authorization': f'Bearer {LINE_NOTIFY_TOKEN}'}
        payload = {'message': f'ตรวจพบใบหน้า: {face_count} คน'}
        files = {'imageFile': image_bytes}

        response = requests.post(LINE_API_URL, headers=headers, data=payload, files=files)

        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': 'Sent to LINE'}), 200
        else:
            # ถ้า LINE ปฏิเสธ ให้ส่ง Error กลับไปบอกหน้าเว็บ
            return jsonify({'status': 'error', 'message': f'LINE API Error: {response.text}'}), 500

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)