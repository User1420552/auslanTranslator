import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from datetime import datetime
import cv2
import mediapipe as mp

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'mp4'}

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image, results


def draw_styled_landmarks(image, results):
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
        if filename.endswith(".mp4"):
            video_url = os.path.join(directory, filename)  # Provide the local file path
            video_files.append({"filename": filename, "url": video_url})
    return video_files


@app.route('/upload-panel', methods=['GET', 'POST'])
def video():
    video_directory = "static/videos"
    video_files = get_video_files(video_directory)
    return render_template('upload_panel.html', video_files=video_files)


@app.route('/upload-panel/<video_filename>')
def video_panel(video_filename):
    selected_video_filename = video_filename
    selected_video_path = os.path.join("static/videos", selected_video_filename)
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        cap = cv2.VideoCapture(selected_video_path)
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('static/videos/' + video_filename + 'translated', fourcc, 30, (frame_width, frame_height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            image, results = mediapipe_detection(frame, holistic)
            draw_styled_landmarks(image, results)
            out.write(image)

        cap.release()
        out.release()

    return render_template('upload_panel_videos.html', selected_video_url=selected_video_path,
                           filename=selected_video_filename, video_rendered=out)


if __name__ == '__main__':
    app.run(debug=True)