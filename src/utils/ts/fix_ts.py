import av

def fix_ts(infile, outfile):
    input_container = av.open(infile, mode="r")
    output_container = av.open(outfile, mode="w")

    try:
        streams = {}
        for in_stream in input_container.streams:
            if in_stream.type not in ("video", "audio"):
                continue

            codec_context = getattr(in_stream, "codec_context", None)
            codec_name = codec_context.name if codec_context and hasattr(codec_context, "name") else None

            if not codec_name and hasattr(in_stream, "codec") and in_stream.codec:
                codec_name = getattr(in_stream.codec, "name", None)

            out_stream = None
            try:
                out_stream = output_container.add_stream(template=in_stream)
            except Exception:
                if codec_name:
                    try:
                        out_stream = output_container.add_stream(codec_name)
                    except Exception:
                        pass

            if out_stream:
                streams[in_stream.index] = out_stream

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
        try:
            output_container.close()
        except Exception:
            pass
        try:
            input_container.close()
        except Exception:
            pass
