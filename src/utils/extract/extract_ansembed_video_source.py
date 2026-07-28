import re
from bs4 import BeautifulSoup
from src.var import print_status

def extract_ansembed_video_source(html_content):
    if not html_content:
        return None
        match = re.search(r'file\s*:\s*["\'](https?://[^"\']+)["\']', html_content)
    if match:
        return match.group(1)
            soup = BeautifulSoup(html_content, 'html.parser')
    script_tags = soup.find_all('script')
    for script in script_tags:
        if script.string and 'jwplayer' in script.string:
            url_match = re.search(r'file\s*:\s*["\'](https?://[^"\']+)["\']', script.string)
            if url_match:
                return url_match.group(1)
                
    print_status("Could not extract video source from AnsEmbed", "warning")
    return None
