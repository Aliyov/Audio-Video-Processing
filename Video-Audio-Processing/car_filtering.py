import librosa
import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter
import argparse, os

# Butterworth low-pass filter function
def butter_lowpass_filter(data, cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, data)

# Main processing function for car audio enhancement
def car_audio_process(input_file, output_file, side_gain=1.5, filter_order=4):
    cutoff = 10000.0  # Low-pass filter cutoff frequency (10,000 Hz)

    # Load stereo audio
    y, sr = librosa.load(input_file, sr=None, mono=False)
    
    if y.shape[0] != 2:
        raise ValueError("Input file must be stereo")

    left = y[0]
    right = y[1]

    # Convert to Mid/Side
    mid = (left + right) / 2
    side = (left - right) / 2

    # Stereo enhancement: amplify side channel
    side *= side_gain

    # Apply Low-Pass filter to side signal
    side = butter_lowpass_filter(side, cutoff, sr, order=filter_order)

    # Convert back to Left/Right
    new_left = mid + side
    new_right = mid - side

    # Stack to stereo array
    output = np.vstack((new_left, new_right))

    # Ensure 'uploads' directory exists
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # Save processed file
    output_file_path = os.path.join('uploads', output_file)
    sf.write(output_file_path, output.T, sr)

    print(f"Processed file saved as {output_file_path}")

# Argument parser
def parse_arguments():
    parser = argparse.ArgumentParser(description="Enhance car stereo audio: side amplification + low-pass filtering.")
    
    parser.add_argument('input_file', type=str, help="Path to the input stereo audio file")
    parser.add_argument('output_file', type=str, help="Path to save the processed audio file")
    parser.add_argument('--side_gain', type=float, default=1.5, help="Gain factor for the side channel (e.g., 1.0 = original, 1.5 = enhanced)")
    parser.add_argument('--filter_order', type=int, default=4, choices=[2, 4, 6, 8], help="Order of the Butterworth low-pass filter")

    return parser.parse_args()

# Main runner
if __name__ == "__main__":
    args = parse_arguments()

    car_audio_process(
        input_file=args.input_file,
        output_file=args.output_file,
        side_gain=args.side_gain,
        filter_order=args.filter_order
    )
