import os
from flask import Flask, render_template, url_for, request
from werkzeug.utils import secure_filename
from datetime import datetime


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
        if filename.endswith(".mp4"):
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

    return render_template('upload_panel_videos.html', selected_video_url=selected_video_url, filename=selected_video_filename)


if __name__ == '__main__':
    app.run(debug=True)
