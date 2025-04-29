# To be note that we used "mp3" for audio part to keep consistency between all processes. We already now that WAV is original version of output but in order to keep
# consistency we convert WAV to mp3 and when possible extract audio as a mp3 from the file.

# Also in order to keep again consistency we made sure that input name and output name of audio file is same so, filtering order doesnt matter. 
# For these reason we used "temp_audio". 


import numpy as np
import tempfile
import os
import shutil
from pydub import AudioSegment
import soundfile as sf
import scipy.ndimage


def apply_wiener_filter(signal, noise_power_db, window_size=5, eps=1e-10):
    noise_power = 10 ** (noise_power_db / 10.0)
    noise_power = np.clip(noise_power, 1e-10, 1e10)

    local_mean = scipy.ndimage.uniform_filter1d(signal, size=window_size, mode='mirror')
    local_square_mean = scipy.ndimage.uniform_filter1d(signal**2, size=window_size, mode='mirror')

    local_var = local_square_mean - local_mean**2
    local_var = np.maximum(local_var, 0)

    factor = (local_var - noise_power) / (local_var + eps)
    factor = np.maximum(factor, 0)

    denoised_signal = local_mean + factor * (signal - local_mean)
    return denoised_signal


# --- Simple delay effect ---
def apply_delay(signal, sr, delay_ms, delay_gain_percent):
    delay_samples = int((delay_ms / 1000.0) * sr)
    delay_gain = delay_gain_percent / 100.0

    output = np.zeros(len(signal) + delay_samples)
    output[:len(signal)] += signal
    output[delay_samples:] += signal * delay_gain

    output /= np.max(np.abs(output))  # Normalize
    return output


# --- Main processing function ---
def denoise_delay(input_file, output_file, noise_power_db, delay_ms, delay_gain_percent):
    print("Processing MP3 with Wiener filter and delay...")

    # Load input MP3 with pydub
    audio = AudioSegment.from_file(input_file, format="mp3").set_channels(1)
    sr = audio.frame_rate

    # Convert to NumPy array (float32, normalized)
    samples = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0

    # Apply processing
    denoised = apply_wiener_filter(samples, noise_power_db)
    processed = apply_delay(denoised, sr, delay_ms, delay_gain_percent)

    # Clip and convert to int16 for saving
    processed = np.clip(processed, -1.0, 1.0)
    processed_int16 = (processed * 32767).astype(np.int16)

    # Write to temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpwav:
        temp_wav_path = tmpwav.name
    sf.write(temp_wav_path, processed_int16, sr)

    # Ensure output directory exists
    uploads_dir = 'uploads'
    os.makedirs(uploads_dir, exist_ok=True)
    output_path = os.path.join(uploads_dir, os.path.basename(output_file))

    # Use a second temporary MP3 file if input and output paths are the same
    if os.path.abspath(input_file) == os.path.abspath(output_path):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpmp3:
            temp_mp3_path = tmpmp3.name
        AudioSegment.from_wav(temp_wav_path).export(temp_mp3_path, format="mp3")
        shutil.move(temp_mp3_path, output_path)
    else:
        AudioSegment.from_wav(temp_wav_path).export(output_path, format="mp3")

    os.remove(temp_wav_path)

    print(f"Processed audio saved to: {output_path}")
