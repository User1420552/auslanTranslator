from flask import redirect, render_template, request, Blueprint, flash
from app.users import db, Users
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename
from matplotlib import pyplot as plt
import time
import mediapipe as mp
from datetime import datetime
import uuid

current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

routes_bp = Blueprint(
    'routes_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@routes_bp.route('/')
def home():
    title = "Home"
    return render_template('home.html')


@routes_bp.route('/upload')
def upload():
    return render_template('upload.html')


@routes_bp.route('/upload-success', methods=['POST'])
def upload_file():
    file_saved_successfully = False
    if 'file' not in request.files:
        return "No file part"

    uploaded_file = request.files['file']

    if uploaded_file.filename == '':
        return "No selected file"

    unique_folder = str(uuid.uuid4())
    folder_path = os.path.join('static')
    file_extension = os.path.splitext(uploaded_file.filename)[-1]
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{uploaded_file}{current_datetime}{file_extension}"
    file_path = os.path.join(folder_path, secure_filename(filename))

    uploaded_file.save(file_path)
    success_message = "File saved successfully"
    return render_template('home.html', success_message=success_message)


@routes_bp.route('/upload-panel')
def upload_panel():
    upload_directory = 'static'

    uploaded_videos = []

    for root, _, files in os.walk(upload_directory):
        for file in files:
            if file.endswith(('.mp4', '.avi', '.mkv')):
                video_path = os.path.join(root, file)
                uploaded_videos.append(video_path)
                print(uploaded_videos)
    return render_template('upload_panel.html', uploaded_videos=uploaded_videos)


@routes_bp.route('/translator')
def translator():

    return render_template('translator.html')
