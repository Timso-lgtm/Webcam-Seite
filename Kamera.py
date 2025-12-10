import cv2
import threading
import time
from flask import Flask, Response, request, render_template_string, redirect
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

app.route('/infos')
def infos():
    with open('Infos.html', 'r', encoding='utf-8') as f:
        return f.read()


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop')
def stop_stream():
    global stream_active
    stream_active = False
    return "Stream ist geschlossen."



@app.route('/stop')
def stop_stream_alias():
    return stop_stream()


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        camera.close()

