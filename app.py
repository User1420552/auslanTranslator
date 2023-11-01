import os
from flask import Flask, render_template, url_for, request
from werkzeug.utils import secure_filename
from datetime import datetime
import cv2


app = Flask(__name__)


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


@app.route('/upload-panel/<video_filename>')
def video_panel(video_filename):
    selected_video_filename = video_filename
    selected_video_url = url_for('static', filename='videos/' + selected_video_filename)
    video_directory = 'static/videos/'
    selected_video_path = os.path.join(video_directory, selected_video_filename)

    if not os.path.exists(selected_video_path):
        return "Selected video does not exist."

    cap = cv2.VideoCapture(selected_video_path)

    if not cap.isOpened():
        return "Unable to read video"

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    output_filename = 'processed_' + selected_video_filename
    output_video_path = os.path.join(video_directory, output_filename)
    processed_video_url = url_for('static', filename='videos/' + output_filename)

    print('new_video_path = ' + output_video_path)
    print('selected_video_path = ' + selected_video_path)
    print('output_video_path = ' + output_video_path)

    fourcc = cv2.VideoWriter_fourcc(*'H264')
    fps = 15

    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    while True:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break

    cap.release()
    out.release()

    if os.path.exists(output_video_path):
        print('Video found')
        return render_template('upload_panel_videos.html', selected_video_url=selected_video_url, processed_video_url=processed_video_url)

    else:
        print('Video not found')
        return 'Video does not exist'


if __name__ == '__main__':
    app.run(debug=True)