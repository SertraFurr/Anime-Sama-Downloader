from utils.var import print_status, Colors
import re
from bs4 import BeautifulSoup
import requests, time, re

def extract_sendvid_video_source(html_content):
    if not html_content:
        return None
    video_source_pattern = r'var\s+video_source\s*=\s*"([^"]+)"'
    match = re.search(video_source_pattern, html_content)
    if match:
        return match.group(1)
    print_status("Could not extract video source from SendVid", "warning")
    return None

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

def extract_vidmoly_video_source(html_content):
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

def unpack_js_for_ts_file(packed_code, base, count, words):
    def to_base(num, base):
        if num == 0:
            return '0'
        digits = []
        while num:
            digits.append(str(num % base) if num % base < 10 else chr(ord('a') + num % base - 10))
            num //= base
        return ''.join(reversed(digits))
    
    replacements = {to_base(i, base): words[i] for i in range(count) if i < len(words) and words[i]}
    unpacked = packed_code
    for key, value in replacements.items():
        pattern = r'\b' + re.escape(key) + r'\b'
        unpacked = re.sub(pattern, value, unpacked)
    
    return unpacked

def extract_packed_code_for_ts(html_content):
    pattern = r"eval\(function\(p,a,c,k,e,d\)\{.*?\}\('(.*?)',(\d+),(\d+),'(.*?)'\.split\('\|'\)\)\)"
    match = re.search(pattern, html_content, re.DOTALL)
    if match:
        return match.group(1), int(match.group(2)), int(match.group(3)), match.group(4).split('|')
    print("No packed JavaScript code found.")
    return None, None, None, None

def fetch_html_for_ts(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': url.split('/embed/')[0],
            'Connection': 'keep-alive',
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None

def extract_hls_url(unpacked_code):
    pattern = r'["\'](/stream/[^"\']*/master\.m3u8[^"\']*)["\']'
    match = re.search(pattern, unpacked_code)
    if match:
        return match.group(1)
    
    print("No matching /stream/.../master.m3u8 URL found in unpacked code.")
    return None

def extract_last_video_source(master_m3u8_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Referer': master_m3u8_url.split('/embed/')[0],
        }
        response = requests.get(master_m3u8_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        master_content = response.text

        pattern = r'#EXT-X-STREAM-INF:.*?RESOLUTION=(\d+)x(\d+).*?\n(.*?\.m3u8)'
        streams = re.findall(pattern, master_content)

        if not streams:
            print("No variant streams found in master.m3u8")
            return None

        streams_sorted = sorted(streams, key=lambda x: int(x[1]), reverse=True)
        best_stream = streams_sorted[0][2]

        base_url = master_m3u8_url.rsplit('/', 1)[0]
        return f"{base_url}/{best_stream}"

    except Exception as e:
        print(f"Error fetching or parsing master.m3u8: {e}")
        return None


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