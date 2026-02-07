import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # อนุญาตให้เว็บเรียก API ได้

# --- CONFIGURATION ---
LINE_NOTIFY_TOKEN = 'd8e/AFRekeAmmuAUWtUJgDKXzQaG5H3bbb+cgjNLbJ+1AnV11aSwaYecMYuIGQH8NmRzuWycg6VyXhdtE82coauugG3n40eEr67urHrksk002PgRPPPabQahe2Q7IVHjK1Ocrb8sX9HlmT4PQN6vNQdB04t89/1O/w1cDnyilFU=' # ใส่ Token ที่นี่

# ✅ [ส่วนที่เพิ่ม] Health Check สำหรับ UptimeRobot
@app.route('/')
def home():
    return "I am awake! (Face Detection Backend)", 200

def send_line_notify(message, image_base64=None):
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {LINE_NOTIFY_TOKEN}'}
    data = {'message': message}
    files = {}

    if image_base64:
        # แปลง Base64 กลับเป็นไฟล์รูปภาพเพื่อส่ง
        try:
            # ตัดส่วน header ของ base64 ออก (data:image/jpeg;base64,...)
            if "base64," in image_base64:
                image_base64 = image_base64.split("base64,")[1]
            
            img_data = base64.b64decode(image_base64)
            files = {'imageFile': img_data}
        except Exception as e:
            print(f"Error decoding image: {e}")

    try:
        response = requests.post(url, headers=headers, data=data, files=files)
        return response.status_code
    except Exception as e:
        print(f"Error sending Line: {e}")
        return 500

@app.route('/detect-action', methods=['POST'])
def detect_action():
    data = request.json
    face_count = data.get('face_count', 0)
    image_data = data.get('image', None) # รับรูป Base64 จากหน้าเว็บ

    print(f"Detected {face_count} faces! Processing notification...")
    
    # ส่งแจ้งเตือน Line
    msg = f"⚠️ ตรวจพบมนุษย์ {face_count} คนในพื้นที่!"
    status = send_line_notify(msg, image_data)

    if status == 200:
        return jsonify({"status": "success", "message": "Notification sent"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to send"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)