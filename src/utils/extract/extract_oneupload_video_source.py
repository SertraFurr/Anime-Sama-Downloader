import re
from bs4 import BeautifulSoup

from src.var import print_status

def extract_oneupload_video_source(html_content):
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
    print_status("Could not extract video source from OneUpload", "warning")
    return None