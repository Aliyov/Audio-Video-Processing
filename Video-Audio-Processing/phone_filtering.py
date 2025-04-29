# To be note that we used "mp3" for audio part to keep consistency between all processes. We already now that WAV is original version of output but in order to keep
# consistency we convert WAV to mp3 and when possible extract audio as a mp3 from the file.

# Also in order to keep again consistency we made sure that input name and output name of audio file is same so, filtering order doesnt matter. 
# For these reason we used "temp_audio". 


import numpy as np
import os
import tempfile
import shutil
from scipy.signal import butter, lfilter
from pydub import AudioSegment
import soundfile as sf
import argparse


# Butterworth band-pass filter
def butter_filter(data, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='bandpass', analog=False)
    return lfilter(b, a, data)

# Main MP3-compatible mid/side processing function
def mid_side_process(input_file, output_file, side_gain=0.5, filter_order=4):
    print("Running Mid/Side Processing with MP3 support...")

    # Convert MP3 to WAV temporarily
    audio = AudioSegment.from_file(input_file, format="mp3")
    if audio.channels != 2:
        raise ValueError("Input file must be stereo")

    sr = audio.frame_rate
    samples = np.array(audio.get_array_of_samples()).reshape((-1, 2)).T  # Shape (2, N)
    samples = samples.astype(np.float32) / 32768.0  # Normalize

    # Convert to Mid/Side
    left, right = samples[0], samples[1]
    mid = (left + right) / 2
    side = (left - right) / 2

    # Side gain and band-pass filter
    side *= side_gain
    side = butter_filter(side, 800.0, 12000.0, sr, order=filter_order)

    # Convert back to Left/Right
    new_left = mid + side
    new_right = mid - side
    stereo_out = np.vstack((new_left, new_right)).T  # Shape (N, 2)

    # Convert to int16 for saving
    stereo_out = np.clip(stereo_out, -1.0, 1.0)
    stereo_out_int16 = (stereo_out * 32767).astype(np.int16)

    # Write to temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpwav:
        temp_wav_path = tmpwav.name
    sf.write(temp_wav_path, stereo_out_int16, sr)

    # Prepare output path
    uploads_folder = 'uploads'
    os.makedirs(uploads_folder, exist_ok=True)
    final_output_path = os.path.join(uploads_folder, os.path.basename(output_file))

    # If input and output are the same, use intermediate temp file
    if os.path.abspath(input_file) == os.path.abspath(final_output_path):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpmp3:
            temp_mp3_path = tmpmp3.name
        AudioSegment.from_wav(temp_wav_path).export(temp_mp3_path, format="mp3")
        shutil.move(temp_mp3_path, final_output_path)
    else:
        AudioSegment.from_wav(temp_wav_path).export(final_output_path, format="mp3")

    os.remove(temp_wav_path)

    print(f"Processed file saved as: {final_output_path}")


# Optional CLI interface
def parse_arguments():
    parser = argparse.ArgumentParser(description="Mid/Side process stereo MP3 with band-pass filtering.")
    parser.add_argument('input_file', type=str, help="Input MP3 file path")
    parser.add_argument('output_file', type=str, help="Output MP3 file path")
    parser.add_argument('--side_gain', type=float, default=0.5, help="Side channel gain (0.0 = mono, 1.0 = original)")
    parser.add_argument('--filter_order', type=int, default=4, choices=[2, 4, 6, 8], help="Butterworth filter order")
    return parser.parse_args()


