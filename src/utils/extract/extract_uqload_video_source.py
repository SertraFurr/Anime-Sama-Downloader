import re
import requests
from src.utils.fetch.fetch_html_for_ts              import fetch_html_for_ts
from src.utils.extract.extract_packed_code_for_ts   import extract_packed_code_for_ts
from src.utils.extract.extract_last_video_source    import extract_last_video_source

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def extract_hls_url(js_code):
    patterns = [
        r'https?://[^"\']+master\.m3u8[^"\']*',
        r'https?://[^"\']+\.m3u8[^"\']*',
        r'/[^"\']+master\.m3u8[^"\']*',
    ]

    for pattern in patterns:
        match = re.search(pattern, js_code)
        if match:
            return match.group(0)

    print("No m3u8 URL found in unpacked code.")
    return None

def encode_base(num: int, base: int) -> str:
    if base > len(ALPHABET):
        raise ValueError(f"Unsupported base {base}. Maximum supported is {len(ALPHABET)}.")
    if num == 0:
        return ALPHABET[0]
    result = ""
    while num:
        result = ALPHABET[num % base] + result
        num //= base
    return result


def unpack_js_for_ts_file(packed_code, base, count, words):
    unpacked = packed_code
    for i in reversed(range(count)):
        if i >= len(words):
            continue

        replacement = words[i]
        if not replacement:
            continue

        token = encode_base(i, base)

        unpacked = re.sub(
            rf'\b{re.escape(token)}\b',
            replacement,
            unpacked
        )

    return unpacked

def extract_m3u8(embed_url):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "fr-FR,fr;q=0.8",
        "cache-control": "no-cache",
        "sec-gpc": "1",
        "upgrade-insecure-requests": "1",
        "user-agent": (
            "Chrome/150.0.0.0 Safari/67.67"
            ),
    }

    response = requests.get(embed_url, headers=headers)
    response.raise_for_status()

    html = response.text

    html_content = fetch_html_for_ts(embed_url, headers=headers)
    if not html_content:
        return None
    packed_code, base, count, words = extract_packed_code_for_ts(html_content)
    if not packed_code:
        return None
    
    unpacked_code = unpack_js_for_ts_file(packed_code, base, count, words)
    
    hls_url = extract_hls_url(unpacked_code)

    if hls_url:
        return hls_url

    return None
