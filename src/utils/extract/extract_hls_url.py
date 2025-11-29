from utils.var import print_status, Colors
import re
from bs4 import BeautifulSoup
import requests, time, re

def extract_hls_url(unpacked_code):
    pattern = r'["\'](/stream/[^"\']*/master\.m3u8[^"\']*)["\']'
    match = re.search(pattern, unpacked_code)
    if match:
        return match.group(1)
    
    print("No matching /stream/.../master.m3u8 URL found in unpacked code.")
    return None