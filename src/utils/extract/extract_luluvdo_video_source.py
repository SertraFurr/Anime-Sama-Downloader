import re
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

def extract_luluvdo_video_source(url, headers=None):
    req_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        res = requests.get(url, headers=req_headers, timeout=10)
        if res.status_code != 200:
            return None

        m3u8_url = None
        m3u8_matches = re.findall(r"['\"](https?://[^\s'\"]+\.m3u8[^\s'\"]*)['\"]", res.text)
        if m3u8_matches:
            m3u8_url = m3u8_matches[0]

        if not m3u8_url:
            pattern = r"eval\(function\(p,a,c,k,e,d\)\{.*?return p\}\('([\s\S]*?)',(\d+),(\d+),'([\s\S]*?)'\.split\('\|'\)"
            match = re.search(pattern, res.text)
            if match:
                p, a, c, k = match.group(1), int(match.group(2)), int(match.group(3)), match.group(4)
                unpacked = unpack_packer(p, a, c, k)
                m3u8_match = re.search(r'["\']?(https?://[^\s"\']+\.m3u8[^\s"\']*)["\']?', unpacked)
                if m3u8_match:
                    m3u8_url = m3u8_match.group(1)

        return m3u8_url
    except Exception:
        return None
