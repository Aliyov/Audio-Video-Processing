# 🎛️ Audio/Video Filter HTTP Server

A Python-based HTTP server with a web frontend for uploading videos, configuring and applying audio/video filters, and streaming the processed video. This project emulates audio processing behaviors such as gain compression, band-pass filtering, and denoising, as well as video effects like grayscale, color inversion, frame interpolation, and upscaling — leveraging Python, FFmpeg, JavaScript, and HTML/CSS.

---

## 📽️ Features

- 📤 **Video Upload:** Upload a single video to the server (one at a time).
- 🗑️ **Video Deletion:** Delete the uploaded video before applying filters.
- 🎚️ **Audio & Video Filter Configuration:** Choose and configure filters via a web interface.
- 🎞️ **Filters Application:** Apply selected filters to the uploaded video.
- 📺 **Streaming:** Stream the filtered video via the web interface.
- 🎛️ **Audio Filters:**
  - Gain Compression
  - Pre-emphasis Filter
  - Band-Pass Filter (Butterworth)
  - Wiener Denoise + Delay
  - Mono/Side Attenuation and Stereo Enhancements
- 🎨 **Video Filters:**
  - Grayscale
  - Color Invert
  - Frame Interpolation (increase FPS)
  - Video Upscaling

---

![Image](https://github.com/user-attachments/assets/e7b261c2-3742-4456-a121-826f0bc1b9b4)

![Image](https://github.com/user-attachments/assets/0cd33085-5451-4f07-a0c0-4f6d90503794)

![Image](https://github.com/user-attachments/assets/25f4e587-bfc6-4218-a5e7-b10a32c21029)

## 📦 Technologies Used

- **Python** — HTTP server, audio processing logic
- **FFmpeg** — video filter processing
- **HTML/CSS/JavaScript** — frontend interface and HTTP request logic
- **Butterworth Filters, Wiener Filters, Pre-emphasis Filters** — custom implementations in Python
- **Fetch API** — for handling HTTP requests from the frontend

---

## How to run?
Clone the repo.
Install necessary tools and libraries with following commands: 

- sudo apt-get install ffmpeg
- pip install -r requirements.txt
- python3 app.py (running backend)
- Enter this url with browser : http://127.0.0.1:5000/

Be sure that 'python' correctly installed on the machine in order to run 'pip' command

