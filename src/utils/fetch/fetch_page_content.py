import requests
from urllib.parse import urlparse

from src.var import print_status

def fetch_page_content(url):
    parsed = urlparse(url)
    referer = f"{parsed.scheme}://{parsed.netloc}/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/108.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': referer
    }
    try:
        print_status("Connecting to server...", "loading")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print_status(f"Failed to connect to {url}: {str(e)}", "error")
        return None
