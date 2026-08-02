import re
import requests
from src.utils.extract.extract_packed_code_for_ts import extract_packed_code_for_ts

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
    m_code = re.search(r'/(?:embed-)?([a-zA-Z0-9]{8,20})(?:\.html)?', embed_url)
    if not m_code:
        return None
    code = m_code.group(1)
    domain_match = re.search(r'https?://([^/]+)', embed_url)
    domain = domain_match.group(1) if domain_match else "uqload.is"
    
    clean_embed_url = f"https://{domain}/embed-{code}.html"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(clean_embed_url, headers=headers, timeout=10)
        if response.status_code == 200:
            m3u8_direct = re.search(r'["\'](https?://[^\s"\']+\.m3u8[^\s"\']*)["\']', response.text)
            if m3u8_direct:
                return m3u8_direct.group(1)
                
            packed_code, base, count, words = extract_packed_code_for_ts(response.text)
            if packed_code:
                unpacked_code = unpack_js_for_ts_file(packed_code, base, count, words)
                hls_url = extract_hls_url(unpacked_code)
                if hls_url:
                    return hls_url
    except Exception:
        pass

    return None
