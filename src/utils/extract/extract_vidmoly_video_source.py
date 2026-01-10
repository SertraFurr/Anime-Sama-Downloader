import re
from src.utils.fetch.fetch_page_content import fetch_page_content
from bs4 import BeautifulSoup
from src.var import print_status

    
def extract_vidmoly_video_hash_source(html_content):
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')

    for script in soup.find_all('script'):
        if script.string and '?g=' in script.string:
            match = re.search(r'\?g=([a-f0-9]{32})', script.string)
            if match:
                return match.group(1)

    return None

def extract_vidmoly_video_source(html_content, page_url):
    hash = extract_vidmoly_video_hash_source(html_content)

    request_url = f"{page_url}?g={hash}"

    html_content = fetch_page_content(request_url)

    if not html_content:
        return None
    soup = BeautifulSoup(html_content, 'html.parser')
    script_tags = soup.find_all('script', type='text/javascript')
    for script in script_tags:
        if script.string and 'jwplayer' in script.string:
            url_match = re.search(r'file:"(https?://.*?)"', script.string)
            if url_match:
                m3u8_url = url_match.group(1)
                return m3u8_url
    print_status("Could not extract video source from Vidmoly", "warning")
    return None
