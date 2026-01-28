import re
from src.utils.fetch.fetch_page_content import fetch_page_content
from bs4 import BeautifulSoup
from src.var import print_status

    
def extract_vidmoly_video_hash_source(html_content):
    if not html_content:
        return None
    match = re.search(r'g=([a-f0-9]{32})', html_content)
    if match:
        return match.group(1)
    return None

def extract_vidmoly_video_source(html_content, page_url):
    if not html_content:
        return None
    def find_file(content):
        if not content: return None
        match = re.search(r'file\s*:\s*["\'](https?://[^"\']+)["\']', content)
        return match.group(1) if match else None
    source = find_file(html_content)
    if source:
        return source
    hash = extract_vidmoly_video_hash_source(html_content)
    if hash:
        request_url = f"{page_url}?g={hash}"
        html_content = fetch_page_content(request_url)
        source = find_file(html_content)
        if source:
            return source
    print_status("Could not extract video source from Vidmoly", "warning")
    return None
