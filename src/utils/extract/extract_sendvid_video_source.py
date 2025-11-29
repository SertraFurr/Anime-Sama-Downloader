import re
import requests
from bs4 import BeautifulSoup

from src.var import print_status, Colors
def extract_sendvid_video_source(html_content):
    if not html_content:
        return None
    video_source_pattern = r'var\s+video_source\s*=\s*"([^"]+)"'
    match = re.search(video_source_pattern, html_content)
    if match:
        return match.group(1)
    print_status("Could not extract video source from SendVid", "warning")
    return None