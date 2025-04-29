import subprocess
import os
import tempfile

def increase_fps(input_file, output_file, fps):
    try:
        if not os.path.exists('uploads'):
            os.makedirs('uploads')

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4", dir='uploads') as temp:
            temp_output = temp.name
        
        ffmpeg_command = [
            'ffmpeg',
            '-y',
            '-i', input_file,
            '-filter_complex', f"[0]minterpolate=fps={fps}:scd=none",
            temp_output
        ]
        
        subprocess.run(ffmpeg_command, check=True)

        os.replace(temp_output, os.path.join('uploads', output_file))
        print(f"Video has been processed and saved as {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while processing the video: {e}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

