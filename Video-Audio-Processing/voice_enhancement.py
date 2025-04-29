# To be note that we used "mp3" for audio part to keep consistency between all processes. We already now that WAV is original version of output but in order to keep
# consistency we convert WAV to mp3 and when possible extract audio as a mp3 from the file.

# Also in order to keep again consistency we made sure that input name and output name of audio file is same so, filtering order doesnt matter. 
# For these reason we used "temp_audio". 


import numpy as np
import os
import tempfile
from scipy.signal import butter, lfilter
from pydub import AudioSegment
import soundfile as sf

# Pre-emphasis filter
def pre_emphasis(signal, alpha=0.97):
    emphasized = np.append(signal[0], signal[1:] - alpha * signal[:-1])
    return emphasized

# Band-pass Butterworth filter (800 Hz – 6000 Hz)
def band_pass_filter(signal, sr, lowcut=800.0, highcut=6000.0, order=4):
    nyq = 0.5 * sr
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return lfilter(b, a, signal)

# Voice enhancement function with MP3 I/O and temp handling
def enhance_voice(input_file, output_file, alpha=0.97, filter_order=4):
    print("Voice-enhancement in progress...")

    # Load MP3 using pydub
    audio = AudioSegment.from_mp3(input_file)
    sr = audio.frame_rate
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)

    if audio.channels > 1:
        samples = samples.reshape((-1, audio.channels))
        samples = samples.mean(axis=1)  # Convert to mono

    samples /= 32768.0  # Normalize to [-1, 1]

    # Apply pre-emphasis and band-pass filter
    emphasized = pre_emphasis(samples, alpha)
    filtered = band_pass_filter(emphasized, sr, 800.0, 6000.0, order=filter_order)

    # Normalize to avoid clipping
    filtered /= np.max(np.abs(filtered) + 1e-10)

    # Convert back to int16 for saving
    filtered_int16 = (filtered * 32767).astype(np.int16)

    # Ensure output directory exists
    uploads_folder = 'uploads'
    os.makedirs(uploads_folder, exist_ok=True)
    final_output_path = os.path.join(uploads_folder, os.path.basename(output_file))

    # Save to temporary WAV and convert to MP3
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpwav:
        temp_wav_path = tmpwav.name
    sf.write(temp_wav_path, filtered_int16, sr)

    if os.path.abspath(input_file) == os.path.abspath(final_output_path):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpmp3:
            temp_mp3_path = tmpmp3.name
        AudioSegment.from_wav(temp_wav_path).export(temp_mp3_path, format="mp3")
        os.replace(temp_mp3_path, final_output_path)
    else:
        AudioSegment.from_wav(temp_wav_path).export(final_output_path, format="mp3")

    os.remove(temp_wav_path)
    print(f"Voice-enhanced audio saved as: {final_output_path}")
