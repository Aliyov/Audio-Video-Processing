import subprocess
import os

def merge_video_audio(video_file, audio_file, output_file):
    """
    Merges a video file and an audio file into a single video with audio.

    Parameters:
        video_file (str): Path to the input video file (without sound).
        audio_file (str): Path to the input audio file.
        output_file (str): Path to the output video file.
    """
    # Ensure output directory exists
    output_folder = os.path.dirname(output_file)
    
    if output_folder and not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        # FFmpeg command to merge video and audio
        ffmpeg_command = [
            'ffmpeg',
            '-y',  # Overwrite output file without asking
            '-i', video_file,
            '-i', audio_file,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            output_file
        ]
        
        # Run the FFmpeg command
        subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ Merged video saved to: {output_file}")

    except subprocess.CalledProcessError as e:
        print("❌ An error occurred while merging video and audio.")
        print(e.stderr.decode())

