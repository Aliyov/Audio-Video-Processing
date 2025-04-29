import subprocess
import os

def convert_to_grayscale(input_file, output_filename):
    try:
        uploads_dir = 'uploads'
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        temp_output = os.path.join(uploads_dir, 'temp_grayscale_video.mp4')
        final_output = os.path.join(uploads_dir, output_filename)

        ffmpeg_command = [
            'ffmpeg',
            '-y',  # Overwrite output file without asking
            '-i', input_file,
            '-vf', 'format=gray',
            temp_output
        ]
        
        subprocess.run(ffmpeg_command, check=True)

        # Replace final output with temp output
        os.replace(temp_output, final_output)

        print(f"Grayscale video saved as {final_output}")
    
    except subprocess.CalledProcessError as e:
        print(f"Error during grayscale conversion: {e}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
