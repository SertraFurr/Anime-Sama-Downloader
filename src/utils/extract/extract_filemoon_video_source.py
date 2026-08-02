import re
import json
import base64
import requests
from urllib.parse import urlparse
from src.var import DEFAULT_USER_AGENT

def b64decode_urlsafe(s):
    s = s.replace('-', '+').replace('_', '/')
    r = len(s) % 4
    if r > 0:
        s += '=' * (4 - r)
    return base64.b64decode(s)

def extract_filemoon_video_source(url, headers=None):
    req_headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Referer": "https://nakanime.tv/",
        "Accept": "application/json, text/plain, */*",
    }
    if headers:
        req_headers.update(headers)

    code_match = re.search(r'/(?:e|d|download|play|v)/([a-zA-Z0-9]+)', url)
    code = code_match.group(1) if code_match else None
    if not code:
        parts = [p for p in url.split('?')[0].split('/') if p]
        if parts:
            code = parts[-1]

    if not code:
        return None

    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else "https://bysesukior.com"

    try:
        api_url = f"{base_url}/api/videos/{code}"
        res = requests.get(api_url, headers=req_headers, timeout=8)
        if res.status_code == 200:
            data = res.json()
            playback = data.get("playback") or data
            
            version_str = str(playback.get("version", ""))
            key_parts = playback.get("key_parts", [])
            iv_b64 = playback.get("iv", "")
            payload_b64 = playback.get("payload", "")

            if version_str and key_parts and iv_b64 and payload_b64:
                version_num = int(version_str)
                a_idx = version_num ^ 0
                i_idx = (31 - version_num) ^ 0

                if 1 <= a_idx <= len(key_parts) and 1 <= i_idx <= len(key_parts):
                    part1 = key_parts[a_idx - 1]
                    part2 = key_parts[i_idx - 1]

                    key_bytes = b64decode_urlsafe(part1) + b64decode_urlsafe(part2)
                    iv_bytes = b64decode_urlsafe(iv_b64)
                    payload_bytes = b64decode_urlsafe(payload_b64)

                    ciphertext = payload_bytes[:-16]
                    tag = payload_bytes[-16:]

                    from Crypto.Cipher import AES
                    cipher = AES.new(key_bytes, AES.MODE_GCM, nonce=iv_bytes)
                    decrypted_bytes = cipher.decrypt_and_verify(ciphertext, tag)
                    decrypted_data = json.loads(decrypted_bytes.decode('utf-8'))

                    sources = decrypted_data.get("sources", [])
                    if sources and isinstance(sources, list):
                        for s in sources:
                            stream_url = s.get("url")
                            if stream_url:
                                return stream_url
    except Exception:
        pass

    try:
        res = requests.get(url, headers=req_headers, timeout=8)
        m3u8_matches = re.findall(r"['\"](https?://[^\s'\"]+\.m3u8[^\s'\"]*)['\"]", res.text)
        if m3u8_matches:
            return m3u8_matches[0]
    except Exception:
        pass

    return None
