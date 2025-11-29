import re
import requests
from bs4 import BeautifulSoup

from src.var import print_status, Colors

def extract_movearnpre_video_source(embed_url):
    url_start = embed_url.split('/embed/')[0]
    html_content = fetch_html_for_ts(embed_url)
    if not html_content:
        return None
    
    packed_code, base, count, words = extract_packed_code_for_ts(html_content)
    if not packed_code:
        return None
    
    unpacked_code = unpack_js_for_ts_file(packed_code, base, count, words)
    
    hls_url = extract_hls_url(unpacked_code)
    if hls_url:
        if hls_url.startswith('/stream/'):
            full_url = url_start + hls_url
            full_url = extract_last_video_source(full_url)
            return full_url

        else:
            print(f"Extracted URL {hls_url} does not match the expected /stream/ pattern.")
    else:
        pass
    
    return None