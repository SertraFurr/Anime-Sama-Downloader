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
        muxed_count = 0

        for packet in input_container.demux():
            st_idx = packet.stream.index
            in_s = packet.stream
            stype = str(getattr(in_s, "type", "")).lower()

            if "data" in stype:
                continue

            if st_idx not in streams:
                out_s = None
                try:
                    out_s = output_container.add_stream(template=in_s)
                except Exception:
                    pass

                if not out_s:
                    codec_name = getattr(getattr(in_s, "codec_context", None), "name", None) or getattr(getattr(in_s, "codec", None), "name", None)
                    if codec_name:
                        try:
                            out_s = output_container.add_stream(codec_name)
                        except Exception:
                            pass

                if not out_s:
                    fallback = "h264" if "video" in stype else "aac"
                    try:
                        out_s = output_container.add_stream(fallback)
                    except Exception:
                        pass

                if out_s:
                    streams[st_idx] = (in_s, out_s)
                else:
                    continue

            in_s, out_s = streams[st_idx]
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
