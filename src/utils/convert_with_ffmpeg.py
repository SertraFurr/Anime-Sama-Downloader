from utils.var import print_status, Colors
import subprocess
import sys

def convert_with_ffmpeg(ts_file, mp4_file):
    print_status(f"Converting {ts_file} to {mp4_file} using ffmpeg...", "loading")
    try:
        subprocess.check_call([
            "ffmpeg", "-y", "-i", ts_file,
            "-c:v", "libx264", "-preset", "ultrafast",
            "-c:a", "aac", mp4_file
        ])
        print_status("Conversion successful using ffmpeg!", "success")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"ffmpeg failed: {e}", "error")
        return False