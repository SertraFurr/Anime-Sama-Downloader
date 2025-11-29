import re
import requests
from urllib.parse import urlparse
from utils.var import print_status

def parse_m3u8_content(m3u8_content, base_url=None):
    streams = []
    lines = m3u8_content.splitlines()
    current_stream = None

    if base_url:
        parsed_url = urlparse(base_url)
        base_path = parsed_url.path.rsplit('/', 1)[0] + '/'
        base_url_without_file = f"{parsed_url.scheme}://{parsed_url.netloc}{base_path}"
        query_params = parsed_url.query

    for line in lines:
        line = line.strip()
        if line.startswith('#EXT-X-STREAM-INF'):
            stream_info = {}
            attributes = re.findall(r'(\w+)=([^,]+)', line)
            for key, value in attributes:
                stream_info[key] = value.strip('"')
            current_stream = stream_info
        elif line.startswith('http') and current_stream:
            current_stream['url'] = line
            streams.append(current_stream)
            current_stream = None
        elif line and not line.startswith('#') and current_stream and base_url:
            if '?' in line:
                full_url = base_url_without_file + line
            else:
                full_url = f"{base_url_without_file}{line}?{query_params}"
            current_stream['url'] = full_url
            streams.append(current_stream)
            current_stream = None
        elif line.startswith('#EXT-X-I-FRAME-STREAM-INF') and base_url:
            iframe_info = {}
            attributes = re.findall(r'(\w+)=([^,]+)', line)
            for key, value in attributes:
                if key == 'URI':
                    uri_value = value.strip('"')
                    if uri_value.startswith('http'):
                        iframe_info['url'] = uri_value
                    else:
                        if '?' in uri_value:
                            iframe_info['url'] = base_url_without_file + uri_value
                        else:
                            iframe_info['url'] = f"{base_url_without_file}{uri_value}?{query_params}"
                else:
                    iframe_info[key] = value.strip('"')
            
            if 'url' in iframe_info:
                streams.append(iframe_info)

    return streams

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