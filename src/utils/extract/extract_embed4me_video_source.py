import re
import json
import binascii
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

KEY = b"kiemtienmua911ca"
IV = b"1234567890oiuytr"

def _decrypt_data(hex_str):
    try:
        data = binascii.unhexlify(hex_str)
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        decrypted = unpad(cipher.decrypt(data), AES.block_size)
        return decrypted.decode('utf-8')
    except Exception:
        return None

def extract_embed4me_video_source(embed_url):
    match = re.search(r'#([a-zA-Z0-9]+)', embed_url)
    if not match:
        match = re.search(r'[?&]id=([a-zA-Z0-9]+)', embed_url)
    if not match:
        return None

    video_id = match.group(1)
    api_url = f"https://lpayer.embed4me.com/api/v1/video?id={video_id}&w=1920&h=1080&r=https://lpayer.embed4me.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Referer": "https://lpayer.embed4me.com/"
    }

    try:
        r = requests.get(api_url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None

        hex_data = r.text.strip()
        if hex_data.startswith('"') and hex_data.endswith('"'):
            hex_data = hex_data[1:-1]

        decrypted = _decrypt_data(hex_data)
        if not decrypted:
            return None

        data = json.loads(decrypted)
        source = data.get('source')
        return source
    except Exception:
        return None
