from flask import Flask, request, jsonify, render_template
from flask import send_from_directory
from phone_filtering import *
from frame_increase import *
from upscale import *
from grayscale import *
from colorInvert import *
from car_filtering import *
from denoise_delay import *
from voice_enhancement import *
from gain_compressor import *
from merge import *
import os, subprocess, re

app = Flask(__name__)

# Set the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

uploaded_video = None


# Route to render index.html
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/settingsSend', methods=['POST'])
def handle_settings():
    try:
        # Get the JSON data from the request
        data = request.get_json()
        print(data)
        # Extract the settings from the received data
        settings_data = data.get('settings', [])
        video_name = data.get('videoName', '')
        print("Received video name:", video_name)
        # Process the settings data (this is just an example)
        print("Received Settings:")
        for setting in settings_data:
            print(setting)
    
        extracted_audio, video_without_audio, video_name = check_and_extract_audio(video_name, settings_data)

        for setting in settings_data:
            if 'PHONELIKEFILTERING' in setting:
                match = re.search(r"PHONELIKEFILTERING \| Settings:\s*(\d+),\s*(\d+)", setting)
                if match:
                    #Extract the two numbers from the match object
                    sideGainValue = float(match.group(1))
                    filterOrder = int(match.group(2))
                    print(f"User Side Gain : {sideGainValue},User Filter Order: {filterOrder}")
                    output_phone = "output_only_sound.mp3"
                    print(f"{extracted_audio}")
                    mid_side_process(extracted_audio, output_phone, sideGainValue, filterOrder)

            elif 'CARLIKEFILTERING' in setting:
                match = re.search(r"CARLIKEFILTERING \| Settings:\s*(\d+),\s*(\d+)", setting)
                if match:
                    #Extract the two numbers from the match object
                    sideGainValue2 = float(match.group(1))
                    filterOrder2 = int(match.group(2))
                    print(f"User Side Gain : {sideGainValue2},User Filter Order: {filterOrder2}")
                    output_car = "output_only_sound.mp3"
                    print(f"{extracted_audio}")
                    car_audio_process(extracted_audio, output_car, sideGainValue2, filterOrder2)

            elif 'DENOISEDELAY' in setting:
                match = re.search(r"DENOISEDELAY \| Settings:\s*(\d+),\s*(\d+),\s*(\d+)", setting)
                if match:
                    noisePower = int(match.group(1))
                    delayMS = int(match.group(2))
                    delayGain = int(match.group(3))
                    output_denoise = "output_only_sound.mp3"
                    denoise_delay(extracted_audio, output_denoise, noisePower, delayMS, delayGain)
            
            elif 'VOICEENHANCE' in setting:
                match = re.search(r"VOICEENHANCE \| Settings:\s*(\d+),\s*(\d+)", setting)
                if match:
                    emhasisAlpha = int(match.group(1))
                    highPass = int(match.group(2))
                    output_emphasis = "output_only_sound.mp3"
                    enhance_voice(extracted_audio, output_emphasis, emhasisAlpha, highPass)

            elif 'GAINCOMPRESSOR' in setting:
                match = re.search(r"GAINCOMPRESSOR \| Settings:\s*(\d+),\s*(\d+)", setting)
                if match:
                    compressorThreshold = int(match.group(1))
                    limiterThreshold = int(match.group(2))
                    output_gain = "output_only_sound.mp3"
                    compress_limit_audio(extracted_audio, output_gain, compressorThreshold, limiterThreshold)

            elif 'FRAMEINCREASE' in setting:
                match = re.search(r"FRAMEINCREASE \| Settings:\s*(\d+)", setting)
                if match:
                    targetFPS = int(match.group(1))
                    output_frame_increase = "output_no_sound_video.mp4"
                    increase_fps(video_without_audio, output_frame_increase, targetFPS)    
            
            elif 'UPSCALE' in setting:
                match = re.search(r"UPSCALE \| Settings:\s*(\d+),\s*(\d+)", setting)
                if match:
                    height_value = int(match.group(1))
                    width_value = int(match.group(2))
                    print(f"User Height: {height_value},User Width: {width_value}")
                    output_upscale = "output_no_sound_video.mp4"
                    upscale_video(video_without_audio, output_upscale, height_value, width_value)
            
            elif 'GRAYSCALE' in setting:
                match = re.search(r"GRAYSCALE ", setting)
                if match:
                    output_grayscale = "output_no_sound_video.mp4"
                    convert_to_grayscale(video_without_audio, output_grayscale)

            elif 'COLORINVERT' in setting:
                match = re.search(r"COLORINVERT ", setting)
                if match:
                    output_colorInvert = "output_no_sound_video.mp4"
                    invert_colors(video_without_audio, output_colorInvert)
            
            
            

        # Respond back with a success message (or any other response you need)
        return jsonify({"message": "Settings received successfully", "status": "success"}), 200
    except Exception as e:
        # If any error occurs, return an error message
        print("Error:", str(e))
        return jsonify({"message": "Error processing request", "status": "error"}), 500



def merge_all():
    output_final = "uploads/final_video.mp4"
    input_audio = "uploads/output_only_sound.mp3"
    input_video = "uploads/output_no_sound_video.mp4"

    merge_video_audio(input_video, input_audio, output_final)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # If file doesn't exist, run merge_all to create it
    if not os.path.exists(file_path):
        merge_all()
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def check_and_extract_audio(video_name, settings_data):
    # Define paths for the audio and video without audio
    extracted_audio_path = os.path.join('uploads', 'extracted_audio.mp3')
    video_without_audio_path = os.path.join('uploads', 'no_audio.mp4')
    original_video_path = os.path.join('uploads', video_name)
    
    # Check if both files exist
    if not os.path.exists(extracted_audio_path) or not os.path.exists(video_without_audio_path):
        print("Files not found, extracting audio and video without audio...")
        extracted_audio, video_without_audio = extract_sound_from_video(settings_data, video_name)
        return extracted_audio, video_without_audio, video_name
    else:
        print("Both files already exist. Skipping extraction.")
        return extracted_audio_path, video_without_audio_path, video_name


@app.route('/uploads', methods=['POST'])
def upload_file():
    global uploaded_video
    print("Video Uploaded")

    if uploaded_video:
        return jsonify({"error": "A video has already been uploaded. Please delete the current video before uploading a new one."})

    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"})

    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(video_path)
    uploaded_video = video_path

    return jsonify({"message": f"Video uploaded successfully: {file.filename}"})




@app.route('/delete', methods=['POST'])
def delete_file():
    upload_folder = 'uploads'
    
    # Check if the uploads folder exists
    if os.path.exists(upload_folder):
        try:
            # Loop through all the files in the uploads folder and remove them
            for filename in os.listdir(upload_folder):
                file_path = os.path.join(upload_folder, filename)
                if os.path.isfile(file_path):  # Check if it's a file
                    os.remove(file_path)
                elif os.path.isdir(file_path):  # If it's a directory, remove it as well
                    shutil.rmtree(file_path)
            
            return jsonify({"message": "All files in the uploads folder deleted successfully."})
        except Exception as e:
            return jsonify({"error": f"Error deleting files: {str(e)}"})
    else:
        return jsonify({"error": "Uploads folder not found."})


def extract_sound_from_video(settings_data, video_name):
    if video_name is not None and settings_data is not None:
        extracted_audio, video_without_audio = extract_audio_video(video_name)
        print(f"{extracted_audio}")
        print(f"{video_without_audio}")
    return extracted_audio, video_without_audio

def extract_audio_video(video_name):
    uploads_folder = 'uploads'
    video_file = os.path.join(uploads_folder, video_name)

    extracted_audio = os.path.join(uploads_folder, "extracted_audio.mp3")
    video_without_audio = os.path.join(uploads_folder, "output_no_sound_video.mp4")

    try:
        print("Extracting audio...")
        subprocess.run([
            "ffmpeg", "-i", video_file, "-vn", "-acodec", "libmp3lame", "-q:a", "2", extracted_audio
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Audio extracted to {extracted_audio}")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode()
        print(f"FFmpeg Error during audio extraction: {error_msg}")
        return None, None

    try:
        print("Removing audio from video...")
        subprocess.run([
            "ffmpeg", "-i", video_file, "-c", "copy", "-an", video_without_audio
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Video without audio saved as {video_without_audio}")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode()
        print(f"Error removing audio: {error_msg}")
        return None, None
    
    return extracted_audio, video_without_audio



if __name__ == '__main__':
    app.run(debug=True)
