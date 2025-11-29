from utils.var import print_status, Colors
import subprocess
import sys
import shutil
import os
import av

def check_ffmpeg_installed():
    return shutil.which("ffmpeg") is not None


# 2e function for check if ffmpeg is installed 
#def check_ffmpeg_installed():
#    try:
#        result = subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True, text=True)
#        print(f"FFmpeg is installed: {result.stdout.splitlines()[0]}")
#        return True
#    except (subprocess.CalledProcessError, FileNotFoundError):
#        print("FFmpeg is not detected in PATH.")
#        return False