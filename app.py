import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- ตั้งค่า Key (ดึงจาก Render) ---
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
IMGBB_API_KEY = os.environ.get('IMGBB_API_KEY')  # เปลี่ยนเป็นชื่อนี้

# URL ของ LINE Messaging API (Broadcast)
LINE_API_URL = 'https://api.line.me/v2/bot/message/broadcast'

def upload_to_imgbb(base64_string):
    """
    ฟังก์ชันเอารูป Base64 ไปฝากไว้ที่ ImgBB
    Return: ลิงก์รูป (URL) หรือ None
    """
    try:
        url = "https://api.imgbb.com/1/upload"
        
        # ตัดส่วนหัว data:image... ออกถ้ามี
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]

        # เตรียมข้อมูลส่ง ImgBB
        payload = {
            "key": IMGBB_API_KEY,
            "image": base64_string
        }
        
        print("🚀 กำลังอัปโหลดรูปไป ImgBB...")
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            result = response.json()
            link = result['data']['url'] # ได้ลิงก์รูปตรงๆ
            print(f"✅ ได้ลิงก์มาแล้ว: {link}")
            return link
        else:
            print(f"❌ ImgBB Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Upload Failed: {e}")
        return None

@app.route('/detect-action', methods=['POST'])
def detect_action():
    try:
        data = request.json
        face_count = data.get('face_count', 0)
        image_base64 = data.get('image', '')

        # เช็คว่าใส่รหัสครบหรือยัง
        if not LINE_CHANNEL_ACCESS_TOKEN or not IMGBB_API_KEY:
             return jsonify({'status': 'error', 'message': 'Missing API Keys in Server'}), 500

        # 1. เอารูปไปฝาก ImgBB
        image_url = upload_to_imgbb(image_base64)
        
        # 2. เตรียมข้อความที่จะส่ง LINE
        messages = []
        
        # ข้อความแจ้งเตือน
        text_msg = {
            "type": "text",
            "text": f"🚨 แจ้งเตือนความปลอดภัย!\n📸 ตรวจพบผู้บุกรุก: {face_count} คน"
        }
        messages.append(text_msg)

        # ถ้าได้รูปจาก ImgBB ก็ส่งรูปไปด้วย
        if image_url:
            image_msg = {
                "type": "image",
                "originalContentUrl": image_url,
                "previewImageUrl": image_url
            }
            messages.append(image_msg)
        else:
            messages.append({"type": "text", "text": "(รูปภาพขัดข้อง แต่ตรวจพบคน!)"})

        # 3. ส่งเข้า LINE Broadcast
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
        }
        payload = {"messages": messages}

        print("📤 กำลังส่งเข้า LINE...")
        response = requests.post(LINE_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': 'Sent OK'}), 200
        else:
            return jsonify({'status': 'error', 'message': f'LINE Error: {response.text}'}), 500

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)