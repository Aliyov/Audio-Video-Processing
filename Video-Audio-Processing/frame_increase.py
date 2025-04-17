import subprocess
import os
import tempfile

def increase_fps(input_file, output_file, fps):
    """
    Interpolates the input video to the desired frame rate using FFmpeg.
    
    Parameters:
    - input_file (str): Path to the input video file.
    - output_file (str): Path where the output video will be saved.
    - fps (int): The target frame rate (user-defined).
    """
    try:
        # Ensure the 'uploads' directory exists
        if not os.path.exists('uploads'):
            os.makedirs('uploads')

        # Generate a temporary output file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4", dir='uploads') as temp:
            temp_output = temp.name
        
        # FFmpeg command to interpolate frames to the specified fps
        ffmpeg_command = [
            'ffmpeg',
            '-y',
            '-i', input_file,
            '-filter_complex', f"[0]minterpolate=fps={fps}:scd=none",
            temp_output
        ]
        
        # Run the FFmpeg command
        subprocess.run(ffmpeg_command, check=True)

        # Replace original file with the new processed video
        os.replace(temp_output, os.path.join('uploads', output_file))
        print(f"Video has been processed and saved as {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while processing the video: {e}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

