# To be note that we used "mp3" for audio part to keep consistency between all processes. We already now that WAV is original version of output but in order to keep
# consistency we convert WAV to mp3 and when possible extract audio as a mp3 from the file.

# Also in order to keep again consistency we made sure that input name and output name of audio file is same so, filtering order doesnt matter. 
# For these reason we used "temp_audio". 

from pydub import AudioSegment
import numpy as np
import soundfile as sf
import tempfile
import shutil
import os
from scipy.signal import butter, lfilter

def butter_lowpass_filter(data, cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, data)

def car_audio_process(input_file, output_file, side_gain=1.5, filter_order=4):
    cutoff = 10000.0  # Low-pass filter cutoff frequency (10,000 Hz)

    # Load MP3 using pydub
    audio = AudioSegment.from_file(input_file, format="mp3")
    audio = audio.set_channels(2)  # Ensure stereo
    sr = audio.frame_rate

    # Get raw data as numpy array
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    samples = samples.reshape((-1, 2)).T  # Shape: (2, num_samples)

    left, right = samples[0], samples[1]

    # Normalize to [-1, 1]
    left /= 32768.0
    right /= 32768.0

    # Convert to Mid/Side
    mid = (left + right) / 2
    side = (left - right) / 2

    # Stereo enhancement
    side *= side_gain

    # Low-pass filter
    side = butter_lowpass_filter(side, cutoff, sr, order=filter_order)

    # Convert back to Left/Right
    new_left = mid + side
    new_right = mid - side

    # Stack and clip
    output = np.vstack((new_left, new_right))
    output = np.clip(output, -1.0, 1.0)

    # Convert back to int16
    output = (output * 32767).astype(np.int16).T  # Shape: (num_samples, 2)

    # Write to temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
        temp_wav_path = tmpfile.name
    sf.write(temp_wav_path, output, sr)

    # Export final MP3
    processed_audio = AudioSegment.from_wav(temp_wav_path)
    output_file_path = os.path.join("uploads", output_file)
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    if os.path.abspath(input_file) == os.path.abspath(output_file_path):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmpmp3:
            temp_mp3_path = tmpmp3.name
        processed_audio.export(temp_mp3_path, format="mp3")
        shutil.move(temp_mp3_path, output_file_path)
    else:
        processed_audio.export(output_file_path, format="mp3")

    os.remove(temp_wav_path)

    print(f"Processed MP3 saved to {output_file_path}")
