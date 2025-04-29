# To be note that we used "mp3" for audio part to keep consistency between all processes. We already now that WAV is original version of output but in order to keep
# consistency we convert WAV to mp3 and when possible extract audio as a mp3 from the file.

# Also in order to keep again consistency we made sure that input name and output name of audio file is same so, filtering order doesnt matter. 
# For these reason we used "temp_audio". 

import numpy as np
import tempfile
import shutil
import os
from pydub import AudioSegment
import soundfile as sf

def db_to_linear(db):
    return 10 ** (db / 20)

def linear_to_db(linear):
    linear = np.maximum(linear, 1e-10)
    return 20 * np.log10(np.abs(linear))

# Compressor + Limiter function
def gain_compressor_limiter(signal, compressor_threshold_db, limiter_threshold_db, ratio=4.0):
    signal = signal.astype(np.float32)
    signal /= 32768.0  # Normalize

    signal_db = linear_to_db(signal)
    compressor_threshold_lin = db_to_linear(compressor_threshold_db)
    limiter_threshold_lin = db_to_linear(limiter_threshold_db)

    compressed_db = np.where(
        signal_db > compressor_threshold_db,
        compressor_threshold_db + (signal_db - compressor_threshold_db) / ratio,
        signal_db
    )

    compressed_lin = db_to_linear(compressed_db)
    compressed_lin = np.clip(compressed_lin, -limiter_threshold_lin, limiter_threshold_lin)

    compressed_lin /= np.max(np.abs(compressed_lin))  # Final normalization
    return (compressed_lin * 32767).astype(np.int16)

# Safe MP3 processing function
def compress_limit_audio(input_file, output_file, compressor_threshold_db, limiter_threshold_db):
    print("Compressing + Limiting...")

    # Load MP3 and convert to mono or stereo depending on original
    audio = AudioSegment.from_file(input_file, format="mp3")
    sr = audio.frame_rate
    channels = audio.channels

    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    if channels == 2:
        samples = samples.reshape((-1, 2)).T  # Shape (2, N)
        processed = np.vstack([
            gain_compressor_limiter(samples[0], compressor_threshold_db, limiter_threshold_db),
            gain_compressor_limiter(samples[1], compressor_threshold_db, limiter_threshold_db)
        ]).T  # Shape (N, 2)
    else:
        processed = gain_compressor_limiter(samples, compressor_threshold_db, limiter_threshold_db)

    # Save to temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        temp_wav_path = tmp.name
    sf.write(temp_wav_path, processed, sr)

    # Prepare output path
    uploads_folder = 'uploads'
    os.makedirs(uploads_folder, exist_ok=True)
    final_output_path = os.path.join(uploads_folder, os.path.basename(output_file))

    # If input and output paths are same, use temp MP3
    if os.path.abspath(input_file) == os.path.abspath(final_output_path):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpmp3:
            temp_mp3_path = tmpmp3.name
        AudioSegment.from_wav(temp_wav_path).export(temp_mp3_path, format="mp3")
        shutil.move(temp_mp3_path, final_output_path)
    else:
        AudioSegment.from_wav(temp_wav_path).export(final_output_path, format="mp3")

    os.remove(temp_wav_path)

    print(f"Processed file saved to: {final_output_path}")
