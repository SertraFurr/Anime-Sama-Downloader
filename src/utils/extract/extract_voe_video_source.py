import re
import json
import base64
import requests
from src.var import DEFAULT_USER_AGENT

def rot13(s):
    res = []
    for c in s:
        o = ord(c)
        if 65 <= o <= 90:
            res.append(chr((o - 65 + 13) % 26 + 65))
        elif 97 <= o <= 122:
            res.append(chr((o - 97 + 13) % 26 + 97))
        else:
            res.append(c)
    return "".join(res)

def voe_decode_payload(payload_str):

    s = rot13(payload_str)
    ops = ['@$', '^^', '~@', '%?', '*~', '!!', '#&']
    for op in ops:
        s = s.replace(op, '')
    s = base64.b64decode(s).decode('utf-8')
    s = "".join(chr(ord(c) - 3) for c in s)
    s = s[::-1]
    s = base64.b64decode(s).decode('utf-8')
    return json.loads(s)


def extract_voe_video_source(single_url, headers=None):

    req_headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Referer": "https://nakanime.tv/"
    }
    if headers:
        req_headers.update(headers)

    try:
        res = requests.get(single_url, headers=req_headers, allow_redirects=True, timeout=8)
        if res.status_code != 200:
            return None

        loc_match = re.search(r'window\.location\.href\s*=\s*["\']([^"\']+)["\']', res.text)
        if loc_match and loc_match.group(1) != single_url and loc_match.group(1) != res.url:
            return extract_voe_video_source(loc_match.group(1), headers)

        html = res.text

        json_match = re.search(r'<script type="application/json">\s*(\[[\s\S]*?\])\s*</script>', html)
        if json_match:
            try:
                json_arr = json.loads(json_match.group(1))
                if json_arr and isinstance(json_arr, list) and len(json_arr) > 0:
                    payload_data = voe_decode_payload(json_arr[0])
                    stream_url = payload_data.get("source") or payload_data.get("direct_access_url")
                    if stream_url and "bigbuckbunny" not in stream_url.lower() and "sample" not in stream_url.lower():
                        return stream_url
            except Exception:
                pass

        m3u8_matches = re.findall(r"['\"](https?://[^\s'\"]+\.m3u8[^\s'\"]*)['\"]", html)
        for m in m3u8_matches:
            if "bigbuckbunny" not in m.lower() and "sample" not in m.lower():
                return m

    except Exception:
        pass

    return None
