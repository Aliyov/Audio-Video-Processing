import subprocess
import os

def invert_colors(input_file, output_filename):
    try:
        uploads_dir = 'uploads'
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        temp_output = os.path.join(uploads_dir, 'temp_inverted_video.mp4')
        final_output = os.path.join(uploads_dir, output_filename)

        ffmpeg_command = [
            'ffmpeg',
            '-y',  # Overwrite output file without asking
            '-i', input_file,
            '-vf', 'negate',  # 'negate' filter inverts colors
            temp_output
        ]
        
        subprocess.run(ffmpeg_command, check=True)

        os.replace(temp_output, final_output)

        print(f"Inverted color video saved as {final_output}")

    except subprocess.CalledProcessError as e:
        print(f"Error during color inversion: {e}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
