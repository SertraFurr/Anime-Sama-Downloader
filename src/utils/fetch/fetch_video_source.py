import time
import requests

from src.var                                            import print_status
from src.utils.parse.parse_m3u8_content                 import parse_m3u8_content
from src.utils.extract.extract_movearnpre_video_source  import extract_movearnpre_video_source
from src.utils.extract.extract_sendvid_video_source     import extract_sendvid_video_source
from src.utils.extract.extract_embed4me_video_source   import extract_embed4me_video_source
from src.utils.extract.extract_oneupload_video_source   import extract_oneupload_video_source
from src.utils.extract.extract_vidmoly_video_source     import extract_vidmoly_video_source
from src.utils.fetch.fetch_page_content                 import fetch_page_content
from src.utils.extract.extract_sibnet_video_source      import extract_sibnet_video_source
from src.utils.fetch.fetch_sibnet_redirect_location     import fetch_sibnet_redirect_location

def fetch_video_source(url):
    def process_single_url(single_url):
        print_status(f"Processing video URL: {single_url[:50]}...", "loading")

        # VIDMOLY DOMAIN FIX
        if 'vidmoly.to' in single_url or 'vidmoly.net' in single_url:
            if 'vidmoly.to' in single_url:
                single_url = single_url.replace('vidmoly.to', 'vidmoly.biz')
            elif 'vidmoly.net' in single_url:
                single_url = single_url.replace('vidmoly.net', 'vidmoly.biz')
            print_status("Converted vidmoly.to to vidmoly.biz", "info")
        
        # SENDVID EXTRACTION
        if 'sendvid.com' in single_url:
            html_content = fetch_page_content(single_url)
            return extract_sendvid_video_source(html_content)

        # EMBED4ME EXTRACTION
        if 'embed4me' in single_url or 'embed4me.com' in single_url or 'lpayer.embed4me.com' in single_url:
            m3u8_url = extract_embed4me_video_source(single_url)
            if not m3u8_url:
                return None
            return m3u8_url
        
        # SIBNET EXTRACTION
        elif 'video.sibnet.ru' in single_url:
            html_content = fetch_page_content(single_url)
            video_source = extract_sibnet_video_source(html_content)
            if video_source:
                print_status("Getting direct download link...", "loading")
                return fetch_sibnet_redirect_location(video_source)
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
        elif 'vidmoly.biz' in single_url:
            attempt = 0
            html_content = None
            
            while True:
                attempt += 1
                html_content = fetch_page_content(single_url)
                if html_content and '<title>Please wait</title>' in html_content and not "url.indexOf('?'" in html_content:
                    print_status(f"Vidmoly rate limit ('Please wait') detected. Retrying in 3s (Attempt {attempt})...", "warning")
                    time.sleep(3)
                    continue
                break
                
            m3u8_url = extract_vidmoly_video_source(html_content, single_url)
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
        for i, single_url in enumerate(url):
            result = process_single_url(single_url)
            results.append(result)
        return results
    else:
        print_status("Invalid input: URL must be a string or a list of strings.", "error")
        return None
