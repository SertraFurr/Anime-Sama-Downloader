from utils.var import print_status, Colors
import subprocess
import sys
import shutil
import os
import av

def print_status(message, status_type="info"):
    prefix = {
        "info": "[*]",
        "success": "[+]",
        "error": "[-]",
        "loading": "[...]"
    }.get(status_type.lower(), "[*]")
    print(f"{prefix} {message}")

def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def check_ffmpeg_installed():
    return shutil.which("ffmpeg") is not None

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


def fix_ts(infile, outfile):
    input_container = av.open(infile, mode="r", format="mpegts")
    output_container = av.open(outfile, mode="w")

    streams = {}
    for in_stream in input_container.streams:
        if not hasattr(in_stream, "codec_context") or in_stream.type == "data":
            continue 
        out_stream = output_container.add_stream(in_stream.codec_context.name)
        streams[in_stream.index] = out_stream

    for packet in input_container.demux():
        if packet.stream.index not in streams:
            continue
        packet.stream = streams[packet.stream.index]
        try:
            output_container.mux(packet)
        except av.PyAVCallbackError:
            continue
        except Exception as e:
            print(f"⚠️ Skipped packet: {e}")


    output_container.close()
    input_container.close()

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