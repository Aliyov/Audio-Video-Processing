import librosa
import numpy as np
import tempfile, os, shutil
from pydub import AudioSegment
import soundfile as sf
import scipy.ndimage  # Import for uniform filter

# Custom Wiener filter implementation with safety checks
def apply_wiener_filter(signal, noise_power_db, window_size=5, eps=1e-10):
    # Convert noise power from dB to linear scale
    noise_power = 10 ** (noise_power_db / 10.0)
    noise_power = np.clip(noise_power, 1e-10, 1e10)

    # Calculate local mean using a moving average filter
    local_mean = scipy.ndimage.uniform_filter1d(
        signal, size=window_size, mode='mirror'
    )

    # Calculate local mean of squared signal
    local_square_mean = scipy.ndimage.uniform_filter1d(
        signal**2, size=window_size, mode='mirror'
    )

    # Calculate local variance and ensure non-negative
    local_var = local_square_mean - local_mean**2
    local_var = np.maximum(local_var, 0)  # Prevent negative variance

    # Compute Wiener filter factor with epsilon regularization
    factor = (local_var - noise_power) / (local_var + eps)
    factor = np.maximum(factor, 0)  # Prevent negative amplification

    # Apply Wiener filter formula
    denoised_signal = local_mean + factor * (signal - local_mean)
    
    return denoised_signal

# Function to apply delay effect (unchanged)
def apply_delay(signal, sr, delay_ms, delay_gain_percent):
    delay_samples = int((delay_ms / 1000.0) * sr)
    delay_gain = delay_gain_percent / 100.0

    output = np.zeros(len(signal) + delay_samples)
    output[:len(signal)] += signal
    output[delay_samples:] += signal * delay_gain

    output /= np.max(np.abs(output))  # Normalize the output
    return output

# Processing function with improved denoising
def denoise_delay(input_file, output_file, noise_power_db, delay_ms, delay_gain_percent):
    print("Denoising with improved Wiener filter + delay...")
    
    # Load audio and convert to mono
    y, sr = librosa.load(input_file, sr=None, mono=True)

    # Apply custom Wiener filter
    denoised_signal = apply_wiener_filter(y, noise_power_db)

    # Apply delay effect
    processed_signal = apply_delay(denoised_signal, sr, delay_ms, delay_gain_percent)

    # Ensure output directory exists
    uploads_folder = 'uploads'
    os.makedirs(uploads_folder, exist_ok=True)

    # Define the path where the final output MP3 file will be saved in the 'uploads' folder
    final_output_path = os.path.join(uploads_folder, os.path.basename(output_file))

    # Safe file handling using temporary files
    if os.path.abspath(input_file) == os.path.abspath(output_file):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            temp_wav = tmpfile.name
        sf.write(temp_wav, processed_signal, sr)
        AudioSegment.from_wav(temp_wav).export(final_output_path, format="mp3")
        os.remove(temp_wav)
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            temp_wav = tmpfile.name
        sf.write(temp_wav, processed_signal, sr)
        AudioSegment.from_wav(temp_wav).export(final_output_path, format="mp3")
        os.remove(temp_wav)

    print(f"Processed audio saved to: {final_output_path}")
