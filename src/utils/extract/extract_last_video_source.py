from utils.var import print_status, Colors
import re
import requests

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