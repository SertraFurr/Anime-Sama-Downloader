import re
from bs4 import BeautifulSoup

from src.var import print_status
def extract_sibnet_video_source(html_content):
    if not html_content:
        return None
    soup = BeautifulSoup(html_content, 'html.parser')
    scripts = soup.find_all('script', type='text/javascript')
    for script in scripts:
        if 'player.src' in script.text:
            match = re.search(r'player\.src\(\[\{.*src:\s*"([^"]+)"', script.text)
            if match:
                video_source = match.group(1)
                if video_source.startswith('//'):
                    video_source = f"https:{video_source}"
                elif not video_source.startswith('https://'):
                    video_source = f"https://video.sibnet.ru{video_source}"
                return video_source
    print_status("Could not extract video source from Sibnet", "warning")
    return None