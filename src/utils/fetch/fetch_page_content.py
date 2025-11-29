import re
import requests
import time

from utils.var                   import print_status

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