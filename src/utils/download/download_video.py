import os
import re
import requests
import time
from tqdm import tqdm
from concurrent.futures                 import ThreadPoolExecutor, as_completed

from src.var                            import Colors, print_status
from src.utils.parse.parse_ts_segments  import parse_ts_segments

def download_video(video_url, save_path, use_ts_threading=False, url='',automatic_mp4=False, threaded_mp4=False):
    print_status(f"Starting download: {os.path.basename(save_path)}", "loading")
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'

    if 'embed4me' in url or 'embed4me' in video_url or 'lpayer.embed4me.com' in url or 'lpayer.embed4me.com' in video_url:
        referer = 'https://lpayer.embed4me.com/'
        origin = 'https://lpayer.embed4me.com'
    elif 'movearnpre.com' in url or 'ovaltinecdn.com' in url:
        referer = 'https://movearnpre.com/'
        origin = ''
    elif 'dingtezuni.com' in url:
        referer = 'https://dingtezuni.com/'
        origin = ''
    elif 'vidmoly.net' in url or 'vidmoly.to' in url:
        referer = 'https://vidmoly.net/'
        origin = ''
    elif 'oneupload.net' in url:
        referer = 'https://oneupload.net/'
        origin = ''
    elif 'sendvid.com' in url:
        referer = 'https://sendvid.com/'
        origin = ''
    elif 'mivalyo.com' in url:
        referer = 'https://mivalyo.com/'
        origin = ''
    else:
        referer = 'https://vidmoly.net/'
        origin = ''

    headers = {
        'User-Agent': ua,
        'Accept': 'video/webm,video/mp4,video/*;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': referer,
    }
    if origin:
        headers['Origin'] = origin

    try:
        if 'm3u8' in video_url:
            from urllib.parse import urljoin

            response = requests.get(video_url, headers=headers, timeout=10)
            response.raise_for_status()
            content = response.text

            if "#EXT-X-STREAM-INF" in content:
                best_bandwidth = -1
                best_url = None
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if line.startswith("#EXT-X-STREAM-INF"):
                        bw_match = re.search(r'BANDWIDTH=(\d+)', line)
                        bw = int(bw_match.group(1)) if bw_match else 0
                        candidate = lines[i+1].strip() if i+1 < len(lines) else None
                        if candidate:
                            if bw > best_bandwidth:
                                best_bandwidth = bw
                                best_url = candidate
                if best_url:
                    if not best_url.startswith('http'):
                        best_url = urljoin(response.url, best_url)
                    variant_resp = requests.get(best_url, headers=headers, timeout=10)
                    variant_resp.raise_for_status()
                    content = variant_resp.text

            segments = []
            base_for_join = response.url
            try:
                if 'variant_resp' in locals():
                    base_for_join = variant_resp.url
            except Exception:
                pass

            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if not line.startswith('http'):
                    seg_url = urljoin(base_for_join, line)
                else:
                    seg_url = line
                segments.append(seg_url)
            if not segments:
                print_status("No .ts segments found in M3U8 playlist", "error")
                return False, None
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            temp_ts_path = save_path.replace('.mp4', '.ts')
            random_string = os.path.basename(save_path).replace('.mp4', '.ts')

            if automatic_mp4 is False and use_ts_threading is False:
                print(f"\n{Colors.BOLD}{Colors.OKCYAN}Threaded Download Option{Colors.ENDC}")
                print_status("Threaded downloading is faster but should not be used on weak Wi-Fi.", "info")
                use_threads = input(f"{Colors.BOLD}Use threaded download for faster performance? (y/n, default: n): {Colors.ENDC}").strip().lower()
                use_threads = use_threads in ['y', 'yes', '1']
            else:
                use_threads = use_ts_threading
            
            if use_threads:
                segment_data = []
                
                def download_segment(segment_url, index):
                    for attempt in range(3):
                        try:
                            seg_response = requests.get(segment_url, headers=headers, stream=True, timeout=10)
                            seg_response.raise_for_status()
                            return index, seg_response.content
                        except requests.RequestException as e:
                            if attempt < 2:
                                time.sleep(2)
                            else:
                                print_status(f"Failed to download segment {index+1}: {str(e)}", "error")
                                return index, None
                    return index, None

                with ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_segment = {executor.submit(download_segment, url, i): i for i, url in enumerate(segments)}
                    with tqdm(total=len(segments), desc=f"📥 {random_string}", unit="segment") as pbar:
                        for future in as_completed(future_to_segment):
                            index, content = future.result()
                            if content is None:
                                print_status(f"Aborting download due to failure in segment {index+1}", "error")
                                return False, None
                            segment_data.append((index, content))
                            pbar.update(1)

                segment_data.sort(key=lambda x: x[0])
                
                with open(temp_ts_path, 'wb') as f:
                    for _, content in segment_data:
                        f.write(content)
            else:
                with open(temp_ts_path, 'wb') as f:
                    for i, segment_url in enumerate(tqdm(segments, desc=f"📥 {random_string}", unit="segment")):
                        for attempt in range(3):
                            try:
                                seg_response = requests.get(segment_url, headers=headers, stream=True, timeout=10)
                                seg_response.raise_for_status()
                                f.write(seg_response.content)
                                break
                            except requests.RequestException as e:
                                if attempt < 2:
                                    time.sleep(2)
                                else:
                                    print_status(f"Failed to download segment {i+1}: {str(e)}", "error")
                                    return False, None
            
            print_status(f"Combined {len(segments)} segments into {temp_ts_path}", "success")
            return True, temp_ts_path
        else:
            response = requests.get(video_url, stream=True, headers=headers, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            
            if response.status_code != 200:
                print_status(f"Download failed with status code: {response.status_code}", "error")
                return False, None
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'wb') as f:
                with tqdm(
                    total=total_size, 
                    unit='B', 
                    unit_scale=True, 
                    desc=f"📥 {os.path.basename(save_path)}",
                    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            print_status(f"Download completed successfully!", "success")
            return True, save_path
    except Exception as e:
        print_status(f"Download failed: {str(e)}", "error")
        return False, None
