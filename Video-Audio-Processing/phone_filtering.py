import librosa
import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter
import argparse, os

# Butterworth filter function (Band-pass filter)
def butter_filter(data, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='bandpass', analog=False)
    return lfilter(b, a, data)

# Main processing function
def mid_side_process(input_file, output_file, side_gain=0.5, filter_order=4):
    # Fixed values for the band-pass filter
    lowcut = 800.0   # Low cutoff frequency (fixed to 800 Hz)
    highcut = 12000.0  # High cutoff frequency (fixed to 12,000 Hz)

    # Load stereo audio
    y, sr = librosa.load(input_file, sr=None, mono=False)
    
    if y.shape[0] != 2:
        raise ValueError("Input file must be stereo")

    left = y[0]
    right = y[1]

    # Convert to Mid/Side
    mid = (left + right) / 2
    side = (left - right) / 2

    # Apply Mono enhancement (side attenuation)
    side *= side_gain  # Adjust the side gain for enhancement

    # Apply Band-Pass filter to the side signal (800 Hz to 12,000 Hz)
    side = butter_filter(side, lowcut, highcut, sr, order=filter_order)

    # Convert back to Left/Right
    new_left = mid + side
    new_right = mid - side

    # Stack to stereo array
    output = np.vstack((new_left, new_right))

    # Ensure the 'uploads' directory exists
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # Save output file inside the 'uploads' folder
    output_file_path = os.path.join('uploads', output_file)
    sf.write(output_file_path, output.T, sr)

    print(f"Processed file saved as {output_file_path}")

# Argument parser to handle command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Process stereo audio to adjust mid/side and apply mono enhancement with band-pass filtering.")
    
    # Add arguments
    parser.add_argument('input_file', type=str, help="Path to the input stereo audio file")
    parser.add_argument('output_file', type=str, help="Path to save the processed audio file")
    parser.add_argument('--side_gain', type=float, default=0.5, help="Gain to apply to the side channel (0.0 = mono, 1.0 = original stereo)")
    parser.add_argument('--filter_order', type=int, default=4, choices=[2, 4, 6, 8], help="Order of the Butterworth filter")

    return parser.parse_args()

# Main function to run the script
if __name__ == "__main__":
    args = parse_arguments()

    mid_side_process(
        input_file=args.input_file,
        output_file=args.output_file,
        side_gain=args.side_gain,
        filter_order=args.filter_order
    )

