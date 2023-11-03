import os
from flask import Flask, render_template, url_for, request
from werkzeug.utils import secure_filename
from datetime import datetime
import numpy as np
import mediapipe as mp
from matplotlib import pyplot as plt
import cv2

app = Flask(__name__)
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/upload-success', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return "No selected file"
    folder_path = os.path.join('static/videos')
    file_extension = os.path.splitext(uploaded_file.filename)[-1]
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{uploaded_file}{current_datetime}{file_extension}"
    file_path = os.path.join(folder_path, secure_filename(filename))
    uploaded_file.save(file_path)
    success_message = "File saved successfully"
    return render_template('home.html', success_message=success_message)


def get_video_files(directory):
    video_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".mp4") and not filename.startswith("processed_"):
            video_url = url_for('static', filename=os.path.join("videos", filename))
            video_files.append({"filename": filename, "url": video_url})
    return video_files


@app.route('/upload-panel', methods=['GET', 'POST'])
def video():
    video_directory = "static/videos"
    video_files = get_video_files(video_directory)
    return render_template('upload_panel.html', video_files=video_files)


def draw_landmarks(image, results):
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION)
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)


def draw_styled_landmarks(image, results):
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION,
                              mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                              mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1)
                              )

    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2)
                              )

    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2)
                              )

    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                              )


def mediapipe_detection(image, holistic):
    # Perform the detection using the holistic object
    results = holistic.process(image)
    return image, results


@app.route('/upload-panel/<video_filename>')
def video_panel(video_filename):
    selected_video_filename = video_filename
    selected_video_url = url_for('static', filename='videos/' + selected_video_filename)
    video_directory = 'static/videos/'
    selected_video_path = os.path.join(video_directory, selected_video_filename)

    if not os.path.exists(selected_video_path):
        return "Selected video does not exist."

    cap = cv2.VideoCapture(selected_video_path)

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    output_filename = 'processed_' + selected_video_filename
    output_video_path = os.path.join(video_directory, output_filename)
    processed_video_url = url_for('static', filename='videos/' + output_filename)

    fourcc = cv2.VideoWriter_fourcc(*'H264')
    fps = 15

    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
    frames = []

    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_array = np.asarray(frame)
            image, results = mediapipe_detection(frame, holistic)
            draw_styled_landmarks(image, results)

            out.write(image)  # Write the processed frame with landmarks to the output video

            frames.append(frame_array)

    cap.release()
    out.release()

    if os.path.exists(output_video_path):
        print('Video found')
        return render_template('upload_panel_videos.html', selected_video_url=selected_video_url,
                               processed_video_url=processed_video_url)


    else:
        print('Video not found')
        return 'Video does not exist'


if __name__ == '__main__':
    app.run(debug=True)
