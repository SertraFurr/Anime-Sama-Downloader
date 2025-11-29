from utils.var import print_status, Colors
import subprocess
import sys
import shutil
import os
import av

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