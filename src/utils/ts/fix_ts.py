import os
import av

def sanitize_ts_file(filepath):
    if not os.path.exists(filepath):
        return False

    file_size = os.path.getsize(filepath)
    if file_size < 188:
        return False

    try:
        with open(filepath, "rb") as f:
            head = f.read(min(file_size, 524288))

        if not head:
            return False

        if head[0] == 0x47 and len(head) >= 377 and head[188] == 0x47 and head[376] == 0x47:
            return False

        sync_offset = -1
        for i in range(min(len(head) - 376, 262144)):
            if head[i] == 0x47 and head[i + 188] == 0x47 and head[i + 376] == 0x47:
                sync_offset = i
                break

        if sync_offset > 0:
            with open(filepath, "rb") as f_in:
                f_in.seek(sync_offset)
                clean_data = f_in.read()
            with open(filepath, "wb") as f_out:
                f_out.write(clean_data)
            return True
    except Exception:
        pass

    return False


def fix_ts(infile, outfile):
    input_container = None
    output_container = None

    open_options = {
        "probesize": "10000000",
        "analyzeduration": "10000000",
        "err_detect": "ignore_err"
    }

    try:
        input_container = av.open(infile, mode="r", options=open_options)
    except Exception:
        sanitize_ts_file(infile)
        try:
            input_container = av.open(infile, mode="r", format="mpegts", options=open_options)
        except Exception:
            try:
                input_container = av.open(infile, mode="r", options=open_options)
            except Exception as final_err:
                raise ValueError(f"Failed to open input file {infile}: {final_err}")

    try:
        output_container = av.open(outfile, mode="w")

        streams = {}
        for in_stream in input_container.streams:
            stype = str(getattr(in_stream, "type", "")).lower()
            if "data" in stype:
                continue

            out_stream = None
            try:
                out_stream = output_container.add_stream(template=in_stream)
            except Exception:
                codec_context = getattr(in_stream, "codec_context", None)
                codec_name = codec_context.name if codec_context and hasattr(codec_context, "name") else None
                if not codec_name and hasattr(in_stream, "codec") and in_stream.codec:
                    codec_name = getattr(in_stream.codec, "name", None)

                if codec_name:
                    try:
                        out_stream = output_container.add_stream(codec_name)
                    except Exception:
                        pass

                if not out_stream:
                    for fallback_codec in ("h264", "aac", "mp3"):
                        try:
                            out_stream = output_container.add_stream(fallback_codec)
                            break
                        except Exception:
                            pass

            if out_stream:
                streams[in_stream.index] = out_stream

        if not streams:
            for in_stream in input_container.streams:
                try:
                    out_stream = output_container.add_stream(template=in_stream)
                    if out_stream:
                        streams[in_stream.index] = out_stream
                except Exception:
                    pass

        if not streams:
            raise ValueError("No valid video or audio streams found in input file.")

        for packet in input_container.demux():
            if packet.stream.index not in streams:
                continue
            packet.stream = streams[packet.stream.index]
            try:
                output_container.mux(packet)
            except av.PyAVCallbackError:
                continue
            except Exception:
                continue

    finally:
        if output_container:
            try:
                output_container.close()
            except Exception:
                pass
        if input_container:
            try:
                input_container.close()
            except Exception:
                pass
