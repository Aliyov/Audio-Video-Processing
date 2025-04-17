import subprocess
import os
import tempfile

def upscale_video(input_file, output_file, width, height):
    """
    Upscales the input video to the specified width and height using FFmpeg.
    
    Parameters:
    - input_file (str): Path to the input video file.
    - output_file (str): Path where the output video will be saved.
    - width (int): The target width for the upscaled video.
    - height (int): The target height for the upscaled video.
    """
    try:
        # Ensure the 'uploads' directory exists
        if not os.path.exists('uploads'):
            os.makedirs('uploads')

        # Generate a temporary output file
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
        
        # Run the FFmpeg command
        subprocess.run(ffmpeg_command, check=True)

        # Replace original file with the new upscaled video
        os.replace(temp_output, os.path.join('uploads', output_file))
        print(f"Video has been upscaled and saved as {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while processing the video: {e}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
