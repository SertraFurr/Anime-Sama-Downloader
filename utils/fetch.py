import re
import requests
import time
from utils.var                   import print_status
from utils.parsers               import parse_m3u8_content
from utils.downloaders.extractor import extract_movearnpre_video_source, extract_sendvid_video_source, extract_sibnet_video_source, extract_oneupload_video_source, extract_vidmoly_video_source

def fetch_episodes(base_url):
    js_url = base_url.rstrip('/') + '/episodes.js'
    print_status("Fetching episode list...", "loading")
    
    try:
        response = requests.get(js_url, timeout=15)
        response.raise_for_status()
        js_content = response.text
    except Exception as e:
        print_status(f"Failed to fetch episodes.js: {str(e)}", "error")
        return None

    pattern = re.compile(r'var\s+(eps\d+)\s*=\s*\[([^\]]*)\];', re.MULTILINE)
    matches = pattern.findall(js_content)
    episodes = {}
    
    for name, content in matches:
        player_num = re.search(r'\d+', name).group()
        player_name = f"Player {player_num}"
        urls = re.findall(r"'(https?://[^']+)'", content)
        episodes[player_name] = urls
    
    if episodes:
        print_status(f"Found {len(episodes)} players with episodes!", "success")
    else:
        print_status("No episodes found in episodes.js", "error")
    
    return episodes

def get_sibnet_redirect_location(video_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/108.0',
        'Accept': 'video/webm,video/mp4,video/*;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://video.sibnet.ru/'
    }
    try:
        response = requests.get(video_url, headers=headers, allow_redirects=False, timeout=10)
        if response.status_code == 302:
            redirect_url = response.headers.get('location')
            if redirect_url.startswith('//'):
                redirect_url = f"https:{redirect_url}"
            return redirect_url
        print_status(f"Expected redirect (302), got {response.status_code}", "warning")
        return None
    except requests.RequestException as e:
        print_status(f"Failed to get redirect location: {str(e)}", "error")
        return None

def fetch_page_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/108.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://sendvid.com/' if 'sendvid.com' in url else 
                  'https://video.sibnet.ru/' if 'video.sibnet.ru' in url else 
                  'https://oneupload.net/' if 'oneupload.net' in url else
                  'https://vidmoly.net/' if 'vidmoly.net' in url else
                  'https://movearnpre.com/' if 'movearnpre.com' in url else
                    'https://mivalyo.com/' if 'mivalyo.com' in url else
                  'https://oneupload.net/' if 'oneupload.net' in url else 
                  'https://vidmoly.net/' if 'vidmoly.to' in url else
                  'https://movearnpre.com/' if 'movearnpre.com' in url or 'ovaltinecdn.com' in url else
                  'https://dingtezuni.com/' if 'dingtezuni.com' in url else
                  'https://smoothpre.com/' if 'smoothpre.com' in url else
                  'https://Smoothpre.com/' if 'Smoothpre.com' in url else
                  'https://mivalyo.com/'
    }
    try:
        print_status("Connecting to server...", "loading")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print_status(f"Failed to connect to {url}: {str(e)}", "error")
        return None

def fetch_video_source(url):
    def process_single_url(single_url):
        print_status(f"Processing video URL: {single_url[:50]}...", "loading")

        # VIDMOLY DOMAIN FIX
        if 'vidmoly.to' in single_url:
            single_url = single_url.replace('vidmoly.to', 'vidmoly.net')
            print_status("Converted vidmoly.to to vidmoly.net", "info")
        
        # SENDVID EXTRACTION
        if 'sendvid.com' in single_url:
            html_content = fetch_page_content(single_url)
            return extract_sendvid_video_source(html_content)
        
        # SIBNET EXTRACTION
        elif 'video.sibnet.ru' in single_url:
            html_content = fetch_page_content(single_url)
            video_source = extract_sibnet_video_source(html_content)
            if video_source:
                print_status("Getting direct download link...", "loading")
                return get_sibnet_redirect_location(video_source)
            return None
        
        # ONEUPLOAD EXTRACTION
        elif 'oneupload.net' in single_url or 'oneupload.to' in single_url:
            single_url = single_url.replace('oneupload.to', 'oneupload.net')
            html_content = fetch_page_content(single_url)
            m3u8_url = extract_oneupload_video_source(html_content)
            if not m3u8_url:
                return None
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/108.0',
                    'Referer': 'https://oneupload.net/'
                }
                response = requests.get(m3u8_url, headers=headers, timeout=10)
                response.raise_for_status()
                streams = parse_m3u8_content(response.text)
                if not streams:
                    print_status("No video streams found in M3U8 playlist", "error")
                    return None
                return max(streams, key=lambda x: int(x.get('BANDWIDTH', 0)))['url']
            except requests.RequestException as e:
                print_status(f"Failed to fetch M3U8 playlist: {str(e)}", "error")
                return None
            
        # VIDMOLY EXTRACTION
        elif 'vidmoly.net' in single_url:
            html_content = fetch_page_content(single_url)
            m3u8_url = extract_vidmoly_video_source(html_content)
            if not m3u8_url:
                return None
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/108.0',
                    'Referer': 'https://vidmoly.net/'
                }
                response = requests.get(m3u8_url, headers=headers, timeout=10)
                response.raise_for_status()
                streams = parse_m3u8_content(response.text)
                if not streams:
                    print_status("No video streams found in M3U8 playlist", "error")
                    return None
                return max(streams, key=lambda x: int(x.get('BANDWIDTH', 0)))['url']
            except requests.RequestException as e:
                print_status(f"Failed to fetch M3U8 playlist: {str(e)}", "error")
                return None
        
        # all those !
        elif 'dingtezuni.com' in single_url or 'mivalyo.com' in single_url or 'smoothpre.com' in single_url or 'Smoothpre.com' in single_url or 'movearnpre.com' in single_url:
            m3u8_url = extract_movearnpre_video_source(single_url)
            if not m3u8_url:
                return None
            return m3u8_url


    if isinstance(url, str):
        return process_single_url(url)
    elif isinstance(url, list):
        results = []
        for single_url in url:
            result = process_single_url(single_url)
            results.append(result)
        return results
    else:
        print_status("Invalid input: URL must be a string or a list of strings.", "error")
        return None
