import os
os.environ['XAUTHORITY'] = '/dev/null'
try:
    from pyvirtualdisplay import Display
    display = Display(visible=0, size=(1080, 1920))
    display.start()
except Exception:
    os.environ['DISPLAY'] = ':0'
import cv2

import numpy as np

import threading

from pathlib import Path

from flask import Flask, render_template, Response, jsonify

from hand_detector import HandDetector

from gesture_engine import GestureEngine

from os_controller import OSController



# ============================================================

# PROJECT PATHS

# ============================================================



# Project structure:

#

# Air canvas/

# ├── backend/

# │   ├── app.py

# │   ├── hand_detector.py

# │   ├── gesture_engine.py

# │   └── os_controller.py

# │

# ├── templates/

# │   └── index.html

# │

# └── static/

#     ├── css/

#     └── js/

# New Code (இப்படி மாத்து):

BASE_DIR = Path(__file__).resolve().parent.parent



TEMPLATE_DIR = BASE_DIR / "frontend" / "templates"

STATIC_DIR = BASE_DIR / "frontend" / "static"



# ============================================================

# FLASK APPLICATION

# ============================================================



app = Flask(

    __name__,

    template_folder=str(TEMPLATE_DIR),

    static_folder=str(STATIC_DIR)

)





# ============================================================

# APPLICATION STATE

# ============================================================



is_active = False

state_lock = threading.Lock()





# ============================================================

# BACKEND ENGINES

# ============================================================



detector = HandDetector(

    max_hands=1,

    detection_con=0.7,

    track_con=0.7

)



engine = GestureEngine()

controller = OSController()





# ============================================================

# WEBCAM

# ============================================================



camera = None





def get_camera():

    global camera



    if camera is None or not camera.isOpened():

        camera = cv2.VideoCapture(0)



        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)



    return camera





def release_camera():

    global camera



    if camera is not None and camera.isOpened():

        camera.release()

        camera = None





# ============================================================

# VIDEO STREAM

# ============================================================



def generate_frames():

    """Generate webcam frames for the browser."""



    global is_active



    while True:



        cam = get_camera()



        success, frame = cam.read()



        if not success:



            blank_frame = cv2.imencode(

                ".jpg",

                np.zeros((480, 640, 3), dtype=np.uint8)

            )[1].tobytes()



            yield (

                b"--frame\r\n"

                b"Content-Type: image/jpeg\r\n\r\n"

                + blank_frame

                + b"\r\n"

            )



            continue



        # Mirror camera

        frame = cv2.flip(frame, 1)



        h, w, _ = frame.shape



        # Get current control state

        with state_lock:

            active_state = is_active



        # ====================================================

        # ACTIVE MODE

        # ====================================================



        if active_state:



            frame, results = detector.find_hands(

                frame,

                draw=True

            )



            landmarks = detector.get_landmark_list(

                results,

                w,

                h

            )



            gesture = engine.detect_gesture(

                landmarks

            )



            # Execute gesture action

            controller.execute_action(

                gesture,

                landmarks,

                w,

                h

            )



            # Status

            status_text = (

                f"CONTROL: ACTIVE | GESTURE: {gesture}"

            )



            cv2.rectangle(

                frame,

                (0, 0),

                (w, 40),

                (0, 0, 0),

                -1

            )



            cv2.putText(

                frame,

                status_text,

                (10, 25),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (0, 255, 0),

                2

            )



        # ====================================================

        # STOPPED MODE

        # ====================================================



        else:



            status_text = "CONTROL: STOPPED"



            cv2.rectangle(

                frame,

                (0, 0),

                (w, 40),

                (0, 0, 0),

                -1

            )



            cv2.putText(

                frame,

                status_text,

                (10, 25),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (0, 0, 255),

                2

            )



        # ====================================================

        # ENCODE FRAME

        # ====================================================



        ret, buffer = cv2.imencode(

            ".jpg",

            frame

        )



        if not ret:

            continue



        frame_bytes = buffer.tobytes()



        yield (

            b"--frame\r\n"

            b"Content-Type: image/jpeg\r\n\r\n"

            + frame_bytes

            + b"\r\n"

        )





# ============================================================

# HOME PAGE

# ============================================================



@app.route("/")

def index():

    return render_template("index.html")





# ============================================================

# VIDEO FEED

# ============================================================



@app.route("/video_feed")

def video_feed():

    return Response(

        generate_frames(),

        mimetype="multipart/x-mixed-replace; boundary=frame"

    )





# ============================================================

# START CONTROL

# ============================================================



@app.route("/start", methods=["POST"])

def start_control():



    global is_active



    with state_lock:

        is_active = True



    return jsonify({

        "status": "active",

        "message": "Gesture control started"

    })





# ============================================================

# STOP CONTROL

# ============================================================



@app.route("/stop", methods=["POST"])

def stop_control():



    global is_active



    with state_lock:

        is_active = False



    return jsonify({

        "status": "inactive",

        "message": "Gesture control stopped"

    })





# ============================================================

# STATUS

# ============================================================



@app.route("/status", methods=["GET"])

def get_status():



    with state_lock:

        active_state = is_active



    return jsonify({

        "status": "active" if active_state else "inactive"

    })





# ============================================================

# HEALTH CHECK

# ============================================================



@app.route("/health")

def health():



    return jsonify({

        "status": "success",

        "message": "Air Canvas backend is running"

    })





# ============================================================

# RUN FLASK SERVER

# ============================================================



if __name__ == "__main__":



    try:



        app.run(

            host="0.0.0.0",

            port=5000,

            debug=False,

            threaded=True

        )



    finally:



        release_camera()
