import subprocess
import os

def invert_colors(input_file, output_filename):
    """
    Inverts the colors of a video using FFmpeg.
    
    Parameters:
    - input_file (str): Path to the input video file.
    - output_filename (str): Name of the output video file (e.g., 'output_inverted.mp4')
    """
    try:
        # Ensure the 'uploads' directory exists
        uploads_dir = 'uploads'
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # Paths for temp and final output
        temp_output = os.path.join(uploads_dir, 'temp_inverted_video.mp4')
        final_output = os.path.join(uploads_dir, output_filename)

        # FFmpeg command to invert video colors
        ffmpeg_command = [
            'ffmpeg',
            '-y',  # Overwrite output file without asking
            '-i', input_file,
            '-vf', 'negate',  # 'negate' filter inverts colors
            temp_output
        ]
        
        # Run the FFmpeg command
        subprocess.run(ffmpeg_command, check=True)

        # Replace final output with temp output
        os.replace(temp_output, final_output)

        print(f"Inverted color video saved as {final_output}")

    except subprocess.CalledProcessError as e:
        print(f"Error during color inversion: {e}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
