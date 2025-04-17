import librosa
import numpy as np
import tempfile
import shutil
import os
from pydub import AudioSegment
import soundfile as sf
import io

def db_to_linear(db):
    return 10 ** (db / 20)

def linear_to_db(linear):
    linear = np.maximum(linear, 1e-10)
    return 20 * np.log10(np.abs(linear))

# Compressor + Limiter function
def gain_compressor_limiter(signal, compressor_threshold_db, limiter_threshold_db, ratio=4.0):
    compressor_threshold_lin = db_to_linear(compressor_threshold_db)
    limiter_threshold_lin = db_to_linear(limiter_threshold_db)

    signal_db = linear_to_db(signal)

    compressed_db = np.where(
        signal_db > compressor_threshold_db,
        compressor_threshold_db + (signal_db - compressor_threshold_db) / ratio,
        signal_db
    )

    compressed_lin = db_to_linear(compressed_db)

    compressed_lin = np.clip(compressed_lin, -limiter_threshold_lin, limiter_threshold_lin)

    compressed_lin /= np.max(np.abs(compressed_lin))

    return compressed_lin

# Full audio processing with safe temp file handling and MP3 output
def compress_limit_audio(input_file, output_file, compressor_threshold_db, limiter_threshold_db):
    print("Compressing in progress...")
    
    # Load the MP3 file with pydub
    audio = AudioSegment.from_mp3(input_file)
    y = np.array(audio.get_array_of_samples(), dtype=np.float32)
    sr = audio.frame_rate

    # Apply the compressor-limiter effect
    processed_signal = gain_compressor_limiter(
        y,
        compressor_threshold_db,
        limiter_threshold_db
    )

    # Ensure the 'uploads' folder exists
    uploads_folder = 'uploads'
    if not os.path.exists(uploads_folder):
        os.makedirs(uploads_folder)

    # Construct the final output path within the 'uploads' folder
    final_output_path = os.path.join(uploads_folder, os.path.basename(output_file))

    # If input and output paths are the same, use a temp file
    if os.path.abspath(input_file) == os.path.abspath(output_file):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            temp_path = tmp.name
        # Save as WAV first
        sf.write(temp_path, processed_signal, sr)
        # Convert WAV to MP3 using pydub
        audio = AudioSegment.from_wav(temp_path)
        audio.export(final_output_path, format="mp3")
        # Clean up temp WAV file
        os.remove(temp_path)
    else:
        # Save as MP3 directly using pydub
        temp_wav_path = tempfile.mktemp(suffix=".wav")
        sf.write(temp_wav_path, processed_signal, sr)
        audio = AudioSegment.from_wav(temp_wav_path)
        audio.export(final_output_path, format="mp3")
        os.remove(temp_wav_path)

    print(f"Compressed + Limited audio saved as: {final_output_path}")
