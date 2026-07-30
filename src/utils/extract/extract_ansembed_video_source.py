import re
from bs4 import BeautifulSoup
from src.var import print_status

def extract_ansembed_video_source(html_content):
    if not html_content:
        return None

    m3u8_matches = re.findall(r"['\"](https?://[^\s'\"]+\.m3u8[^\s'\"]*)['\"]", html_content)
    if m3u8_matches:
        for m in m3u8_matches:
            if "bigbuckbunny" not in m.lower() and "sample" not in m.lower():
                return m

    match = re.search(r'file\s*:\s*["\']?(https?://[^\s\'",]+)["\']?', html_content)
    if match:
        return match.group(1)

    soup = BeautifulSoup(html_content, 'html.parser')
    script_tags = soup.find_all('script')
    for script in script_tags:
        if script.string and ('jwplayer' in script.string or 'm3u8' in script.string):
            url_match = re.search(r'["\'](https?://[^\s\'"]+\.m3u8[^\s\'"]*)["\']', script.string)
            if url_match:
                return url_match.group(1)

    print_status("Could not extract video source from AnsEmbed", "warning")
    return None
