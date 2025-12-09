import requests

from src.var import print_status

def fetch_sibnet_redirect_location(video_url):
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