import re
import base64
import requests

def unpack_packer(p, a, c, k, e=None, d=None):
    def baseN(num, b):
        return ((num == 0) and "0") or (baseN(num // b, b).lstrip("0") + "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"[num % b])
    
    k = k.split('|')
    while c:
        c -= 1
        key = baseN(c, a)
        if k[c]:
            p = re.sub(r'\b' + key + r'\b', k[c], p)
    return p

def decode_vidzy_src(encoded_str, key_bytes):
    raw = base64.b64decode(encoded_str)
    out = bytearray(len(raw))
    for i in range(len(raw)):
        out[i] = raw[i] ^ key_bytes[i % len(key_bytes)]
    return out.decode('utf-8', errors='replace')

def extract_vidzy_video_source(url, headers=None):
    req_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://nakanime.tv/"
    }
    if headers:
        req_headers.update(headers)

    try:
        res = requests.get(url, headers=req_headers, timeout=10)
        if res.status_code != 200:
            return None

        m3u8_matches = re.findall(r"['\"](https?://[^\s'\"]+\.m3u8[^\s'\"]*)['\"]", res.text)
        if m3u8_matches:
            return m3u8_matches[0]

        pattern = r"eval\(function\(p,a,c,k,e,d\)\{.*?return p\}\('([\s\S]*?)',(\d+),(\d+),'([\s\S]*?)'\.split\('\|'\)"
        match = re.search(pattern, res.text)
        if match:
            p, a, c, k = match.group(1), int(match.group(2)), int(match.group(3)), match.group(4)
            unpacked = unpack_packer(p, a, c, k)
            
            key_match = re.search(r'var\s+k\s*=\s*\[([\d\s,]+)\]', unpacked)
            str_match = re.search(r'\}\)\(["\']([A-Za-z0-9+/=]+)["\']\)', unpacked)
            if key_match and str_match:
                key_list = [int(x.strip()) for x in key_match.group(1).split(',')]
                encoded_str = str_match.group(1)
                decoded_url = decode_vidzy_src(encoded_str, key_list)
                if decoded_url and "m3u8" in decoded_url:
                    return decoded_url

        return None
    except Exception:
        return None
