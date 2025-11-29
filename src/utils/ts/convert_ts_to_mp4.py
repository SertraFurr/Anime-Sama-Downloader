from utils.var import print_status, Colors
import subprocess
import sys
import shutil
import os
import av

def convert_ts_to_mp4(input_path, output_path, pre_selected_tool=None):
    if not os.path.exists(input_path):
        print_status(f"Input file {input_path} does not exist", "error")
        return False, input_path
    if os.path.exists(output_path):
        print_status(f"Output file {output_path} already exists. deleting...", "error")
        try:
            os.remove(output_path)
        except Exception as e:
            print_status(f"Failed to delete existing output file: {e}", "error")
            return False, input_path
    if pre_selected_tool == 'ffmpeg':
        try:

            output_path = os.path.splitext(input_path)[0] + '.mp4'
            ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-c:v", "copy",
            "-c:a", "copy",
            output_path
        ]
            print_status(f"Running FFmpeg command: {' '.join(ffmpeg_cmd)}", "info")
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            for line in process.stdout:
                print(line, end='')
            process.wait()
            if process.returncode == 0:
                print_status(f"Video converted successfully to {output_path}", "success")
                return True, output_path
            else:
                print_status("FFmpeg conversion failed", "error")
                return False, input_path
        except Exception as e:
            print_status(f"FFmpeg conversion failed: {str(e)}", "error")
            return False, input_path
    
    elif pre_selected_tool == 'av':
        try:
            fix_ts(input_path, output_path)
            print_status(f"Video converted successfully to {output_path}", "success")
            return True, output_path
        except Exception as e:
            print_status(f"AV conversion failed: {str(e)}", "error")
            return False, input_path

    else:
        print_status("No valid conversion tool specified", "error")
        return False, input_path