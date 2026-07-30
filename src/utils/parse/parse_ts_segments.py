import re
from urllib.parse import urljoin

def parse_ts_segments(m3u8_content, base_url=None):
    segments = []
    lines = m3u8_content.splitlines()
    encryption_detected = False

    map_match = re.search(r'#EXT-X-MAP:URI=["\']?([^"\',\s]+)["\']?', m3u8_content)
    if map_match:
        init_uri = map_match.group(1)
        if base_url and not init_uri.startswith('http'):
            init_uri = urljoin(base_url, init_uri)
        segments.append(init_uri)

    for line in lines:
        line = line.strip()

        if not line or line.startswith('#'):
            if line.startswith('#EXT-X-KEY'):
                encryption_detected = True
            continue

        if line.startswith('http'):
            segments.append(line)
        elif base_url:
            segments.append(urljoin(base_url, line))

    if encryption_detected:
        print("⚠️ M3U8 contains encryption (#EXT-X-KEY). Decryption is not supported.")
    
    return segments
