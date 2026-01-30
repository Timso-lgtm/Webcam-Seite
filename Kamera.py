import cv2
import threading
import time
from flask import Flask, Response, request, render_template_string, redirect, send_from_directory
from picamera import PiCamera
from picamera.array import PiRGBArray

app = Flask(__name__, static_folder='.')
app.secret_key = 'roboter_secret_key'  # Für Sessions


# Kamera-Setup (PiCamera für Pi, oder cv2 für Webcam)
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 20
raw_capture = PiRGBArray(camera, size=(640, 480))


# Gesichtserkennung 
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


# Globale Variablen
current_camera = 0  # 0: PiCamera
stream_active = True

def detect_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return frame

def generate_frames():
    global current_camera
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        if not stream_active:
            break
        image = frame.array
        image = detect_faces(image)  # Gesichtserkennung anwenden
        ret, buffer = cv2.imencode('.jpg', image)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        raw_capture.truncate(0)
        time.sleep(0.1)  # Frame-Rate kontrollieren

@app.route('/<filename>.png')
def serve_png(filename):
    return send_from_directory('.', f'{filename}.png')

@app.route('/styl.css')
def serve_css():
    return send_from_directory('.', 'styl.css')

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def index():
    return redirect('/home')

@app.route('/home')
def home():
    with open('Home.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webcam')
def webcam():
    with open('Webcam.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/team')
def team():
    with open('Team.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/infos')
def infos():
    with open('Infos.html', 'r', encoding='utf-8') as f:
        return f.read()
        
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop')
def stop_stream():
    camera.release()
    return "Stream gestoppt"

@app.route('/start')
def start_stream():
    global camera
    if not camera.isOpened():
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 20)
    return "Stream gestartet"

if __name__ == '__main__':
    print("Webcam-Server gestartet!")
    print("Browser: http://localhost:5000")
    print("Für Handy: http://[PC-IP]:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

