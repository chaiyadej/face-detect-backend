# app.py (สำหรับ LINE Messaging API - Broadcast)
import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 1. เปลี่ยนชื่อตัวแปรให้ตรงกับ Messaging API
# (ต้องไปแก้ใน Render Environment Variables ด้วยนะครับ)
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

# 2. URL สำหรับ Broadcast (ถูกต้องตามที่คุณบอก)
LINE_API_URL = 'https://api.line.me/v2/bot/message/broadcast'

@app.route('/detect-action', methods=['POST'])
def detect_action():
    try:
        data = request.json
        face_count = data.get('face_count', 0)
        
        # หมายเหตุ: Messaging API แบบ Broadcast ส่งรูปโดยตรงไม่ได้
        # ต้องฝากรูปไว้ที่อื่นแล้วส่งเป็น Link เท่านั้น
        # เบื้องต้นเราจะส่งเป็น "ข้อความ" เพื่อแจ้งเตือนก่อนครับ
        
        if not LINE_CHANNEL_ACCESS_TOKEN:
             print("Error: Token missing")
             return jsonify({'status': 'error', 'message': 'Token missing'}), 500

        # 3. เตรียมข้อมูลส่ง LINE (เปลี่ยนรูปแบบเป็น JSON)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
        }

        # ข้อความที่จะส่ง
        payload = {
            "messages": [
                {
                    "type": "text",
                    "text": f"🚨 แจ้งเตือนความปลอดภัย!\n📸 ตรวจพบใบหน้า: {face_count} คน\n(ขณะนี้ระบบรองรับการแจ้งเตือนแบบข้อความ)"
                }
            ]
        }

        # 4. ยิง Request ไปที่ LINE
        print(f"Broadcasting to LINE...")
        response = requests.post(LINE_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': 'Broadcast sent'}), 200
        else:
            print(f"LINE Error: {response.text}")
            return jsonify({'status': 'error', 'message': f'LINE API Error: {response.text}'}), 500

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)