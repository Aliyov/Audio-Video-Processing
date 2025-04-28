import librosa
import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter
import tempfile
import os
from pydub import AudioSegment

# Pre-emphasis filter function
def pre_emphasis(signal, alpha=0.97):
    emphasized = np.append(signal[0], signal[1:] - alpha * signal[:-1])
    return emphasized

# Band-pass Butterworth filter function (800-6000 Hz)
def band_pass_filter(signal, sr, lowcut=800.0, highcut=6000.0, order=4):
    nyq = 0.5 * sr
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    filtered = lfilter(b, a, signal)
    return filtered

# Full voice enhancement processing function with temp file safety and MP3 output
def enhance_voice(input_file, output_file, alpha=0.97, filter_order=4):
    print("Voice-enhancement in progress...")

    # Load the MP3 file with pydub
    audio = AudioSegment.from_mp3(input_file)
    y = np.array(audio.get_array_of_samples(), dtype=np.float32)
    sr = audio.frame_rate

    # Apply pre-emphasis
    emphasized_signal = pre_emphasis(y, alpha)

    # Apply band-pass filter
    enhanced_signal = band_pass_filter(emphasized_signal, sr, lowcut=800.0, highcut=6000.0, order=filter_order)

    # Normalize to avoid clipping
    enhanced_signal /= np.max(np.abs(enhanced_signal))

    # Ensure the 'uploads' folder exists
    uploads_folder = 'uploads'
    if not os.path.exists(uploads_folder):
        os.makedirs(uploads_folder)

    # Construct the final output path within the 'uploads' folder
    final_output_path = os.path.join(uploads_folder, os.path.basename(output_file))

    # If input and output paths are the same, use a temp file
    if os.path.abspath(input_file) == os.path.abspath(output_file):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            temp_output_path = tmpfile.name
        # Write to temporary WAV file
        sf.write(temp_output_path, enhanced_signal, sr)
        # Convert WAV to MP3 using pydub
        audio = AudioSegment.from_wav(temp_output_path)
        audio.export(final_output_path, format="mp3")
        os.remove(temp_output_path)  # Clean up temporary WAV file
    else:
        # Save as temporary WAV file first
        temp_wav_path = tempfile.mktemp(suffix=".wav")
        sf.write(temp_wav_path, enhanced_signal, sr)
        # Convert WAV to MP3 using pydub
        audio = AudioSegment.from_wav(temp_wav_path)
        audio.export(final_output_path, format="mp3")
        os.remove(temp_wav_path)  # Clean up temporary WAV file

    print(f"Voice-enhanced audio saved as: {final_output_path}")