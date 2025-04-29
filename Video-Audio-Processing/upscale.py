import subprocess
import os
import tempfile

def upscale_video(input_file, output_file, width, height):
    try:
        if not os.path.exists('uploads'):
            os.makedirs('uploads')

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4", dir='uploads') as temp:
            temp_output = temp.name

        # FFmpeg command to upscale the video
        ffmpeg_command = [
            'ffmpeg',
            '-y',
            '-i', input_file,
            '-vf', f'scale={width}:{height}',  # Use specified width and height
            '-c:v', 'libx264',  # Set video codec
            '-crf', '23',  # Set CRF (Constant Rate Factor) for quality (lower is better quality)
            '-preset', 'fast',  # Set encoding speed (faster encoding)
            '-c:a', 'aac',  # Set audio codec
            '-b:a', '192k',  # Set audio bitrate
            temp_output
        ]
        
        subprocess.run(ffmpeg_command, check=True)

        os.replace(temp_output, os.path.join('uploads', output_file))
        print(f"Video has been upscaled and saved as {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while processing the video: {e}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
