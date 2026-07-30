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

    sanitize_ts_file(infile)

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
        try:
            input_container = av.open(infile, mode="r", format="mpegts", options=open_options)
        except Exception as final_err:
            raise ValueError(f"Failed to open input file {infile}: {final_err}")

    try:
        output_container = av.open(outfile, mode="w")

        streams = {}
        for in_stream in input_container.streams:
            stype = str(getattr(in_stream, "type", "")).lower()
            if "data" in stype:
                continue

            codec_context = getattr(in_stream, "codec_context", None)
            codec_name = codec_context.name if codec_context and hasattr(codec_context, "name") else None
            if not codec_name and hasattr(in_stream, "codec") and in_stream.codec:
                codec_name = getattr(in_stream.codec, "name", None)

            if codec_name:
                try:
                    out_stream = output_container.add_stream(codec_name)
                    streams[in_stream.index] = (in_stream, out_stream)
                except Exception:
                    pass

        if not streams:
            raise ValueError("No valid video or audio streams found in input file.")

        muxed_count = 0
        for packet in input_container.demux():
            if packet.stream.index not in streams:
                continue

            in_s, out_s = streams[packet.stream.index]
            packet.stream = out_s

            try:
                output_container.mux(packet)
                muxed_count += 1
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

    out_size = os.path.getsize(outfile) if os.path.exists(outfile) else 0
    if muxed_count == 0 or out_size < 10240:
        if os.path.exists(outfile):
            try:
                os.remove(outfile)
            except Exception:
                pass
        raise ValueError(f"PyAV conversion produced empty/invalid file ({muxed_count} packets muxed, {out_size} bytes).")
