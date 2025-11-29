import re

from src.var import print_status

def parse_ts_segments(m3u8_content):
    segments = []
    lines = m3u8_content.splitlines()
    encryption_detected = False

    for line in lines:
        line = line.strip()

        if not line or line.startswith('#'):
            if line.startswith('#EXT-X-KEY'):
                encryption_detected = True
            continue

        if re.match(r'^https?://', line):
            segments.append(line)

    if encryption_detected:
        print("⚠️ M3U8 contains encryption (#EXT-X-KEY). Decryption is not supported.")
    
    return segments