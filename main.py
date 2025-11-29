import re
import os
import sys
import subprocess
import shutil
import sys
import subprocess
import os
import platform
import subprocess
import urllib.request
import zipfile
import tarfile
import shutil
from concurrent.futures                                 import ThreadPoolExecutor, as_completed

# import functions with files
from src.utils.parse.parse_ts_segments                  import parse_ts_segments
from src.utils.ts.convert_ts_to_mp4                     import convert_ts_to_mp4
from src.utils.fetch.fetch_episodes                     import fetch_episodes
from src.utils.fetch.fetch_video_source                 import fetch_video_source
from src.utils.download.download_video                  import download_video
from src.utils.print.print_episodes                     import print_episodes
from src.utils.get.get_player_choice                    import get_player_choice
from src.utils.get.get_episode_choice                   import get_episode_choice
from src.utils.print.print_status                       import print_status
from src.utils.check.check_package                      import check_package
from src.utils.check.check_ffmpeg_installed             import check_ffmpeg_installed
from src.utils.validate_anime_sama_url                  import validate_anime_sama_url
from src.utils.extract.extract_anime_name               import extract_anime_name
from src.utils.get.get_save_directory                   import get_save_directory
from src.utils.download.download_episode                import download_episode
from src.var                                            import Colors, print_separator, print_header, print_tutorial

# PLEASE DO NOT REMOVE: Original code from https://github.com/sertrafurr/Anime-Sama-Downloader

def main():

    if not check_package(ask_install=True, first_run=True):
        print_status("Some required packages were missing. Would you like to install them now? (y/n): ", "warning")

        ask_user = input().strip().lower()
        
        if ask_user in ['y', 'yes', '1']:
            if not check_package(ask_install=True, first_run=False):
                print_status("Failed to install required packages. Please install them manually and re-run the script.", "error")
                sys.exit(1)
        else:
            print_status("Cannot proceed without required packages. Exiting.", "warning")
            input("Press Enter to exit...")
            sys.exit(1)

    if not check_ffmpeg_installed():
        print_status("FFmpeg is not installed or not found in the PATH. You could consider installing it from https://ffmpeg.org/download.html", "error")

    try:
        print_header()
        
        show_tutorial = input(f"{Colors.BOLD}Show tutorial? (y/n, default: n): {Colors.ENDC}").strip().lower()
        if show_tutorial in ['y', 'yes', '1']:
            print_tutorial()
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}{Colors.HEADER}🔗 ANIME-SAMA URL INPUT{Colors.ENDC}")
        print_separator()
        
        while True:
            base_url = input(f"{Colors.BOLD}Enter the complete anime-sama URL: {Colors.ENDC}").strip()
            
            if not base_url:
                print_status("URL cannot be empty", "error")
                continue
                
            is_valid, error_msg = validate_anime_sama_url(base_url)
            if not is_valid:
                print_status(error_msg, "error")
                print_status("Example: https://anime-sama.fr/catalogue/roshidere/saison1/vostfr/", "info")
                continue
            
            break
        
        anime_name = extract_anime_name(base_url)
        print_status(f"Detected anime: {anime_name}", "info")
        
        episodes = fetch_episodes(base_url)
        if not episodes:
            print_status("Failed to fetch episodes. Please check the URL and try again.", "error")
            return 1
        
        print_episodes(episodes)
        
        player_choice = get_player_choice(episodes)
        if not player_choice:
            return 1
        
        episode_indices = get_episode_choice(episodes, player_choice)
        if episode_indices is None:
            return 1
        
        save_dir = get_save_directory()
        
        if isinstance(episode_indices, int):
            episode_indices = [episode_indices]
        
        urls = [episodes[player_choice][index] for index in episode_indices]
        episode_numbers = [index + 1 for index in episode_indices]
        
        print(f"\n{Colors.BOLD}{Colors.HEADER}🎬 PROCESSING EPISODES{Colors.ENDC}")
        print_separator()
        print_status(f"Player: {player_choice}", "info")
        print_status(f"Episodes selected: {', '.join(map(str, episode_numbers))}", "info")
        
        video_sources = fetch_video_source(urls)
        if not video_sources:
            print_status("Could not extract video sources for selected episodes", "error")
            return 1
        
        if isinstance(video_sources, str):
            video_sources = [video_sources]
        use_threading = False
        use_ts_threading = False
        automatic_mp4 = False
        pre_selected_tool = None

        if len(episode_indices) > 1:
            thread_choice = input(f"{Colors.BOLD}Download all episodes simultaneously (threaded) or sequentially? (t/1/y = yes / s = no , default: s): {Colors.ENDC}").strip().lower()
            use_threading = thread_choice in ['t', 'threaded', '1', 'y', 'yes']

        if any('m3u8' in src for src in video_sources if src):
            if use_threading:
                print_status("Because you use threading episodes downloads, M3U8 sources should be downloaded in paralle!", "warning")
            ts_thread_choice = input(f"{Colors.BOLD}M3U8 sources detected. Download .ts files simultaneously (threaded) or sequentially? Will make it near 10x faster. (t/1/y = yes / s = no , default: s): {Colors.ENDC}").strip().lower()
            use_ts_threading = ts_thread_choice in ['t', 'threaded', '1', 'y', 'yes']

        if any('m3u8' in src for src in video_sources if src):
            auto_mp4_choice = input(f"{Colors.BOLD}Convert .ts file(s) to .mp4 automatically after download? (t/1/y = yes / s = no , default: s): {Colors.ENDC}").strip().lower()
            automatic_mp4 = auto_mp4_choice in ['t', 'threaded', '1', 'y', 'yes']

            if automatic_mp4:
                try:
                    import av
                except ImportError:

                    print_status("AV not installed, cannot convert to .mp4. Install it using 'pip install av'", "warning")
                    automatic_mp4 = False

            if automatic_mp4:
                while True:
                    ffmpeg_or_moviepy = input(f"{Colors.BOLD}Choose conversion tool - 1 for AV (fast and easier)  Choose conversion tool - 2 for ffmpeg but takes more space (fast) (default: 1): {Colors.ENDC}").strip().lower()
                    if ffmpeg_or_moviepy in ['1', 'ffmpeg', '']:
                        try :
                            import av
                            pre_selected_tool = 'av'
                            break
                        except ImportError:
                            input("⚠️ AV not installed, cannot use it. Press Enter to quit...")
                            quit()
                    elif ffmpeg_or_moviepy in ['2', 'ffmpeg']:
                        if not check_ffmpeg_installed():
                            print_status("ffmpeg is not installed. Fallback to av", "error")
                            pre_selected_tool = 'av'
                            break
                        break
                    else:
                        print_status("Invalid choice. Please enter 1 for av or enter 2 for ffmpeg (default: 1).", "warning")

        failed_downloads = 0
        try:
            if use_threading and len(episode_indices) > 1:
                print_status("Starting threaded downloads...", "info")
                with ThreadPoolExecutor() as executor:
                    future_to_episode = {
                        executor.submit(download_episode, ep_num, url, video_src, anime_name, save_dir, use_ts_threading, automatic_mp4, pre_selected_tool): ep_num
                        for ep_num, url, video_src in zip(episode_numbers, urls, video_sources)
                    }
                    for future in as_completed(future_to_episode):
                        ep_num = future_to_episode[future]
                        try:
                            success, _ = future.result()
                            if not success:
                                failed_downloads += 1
                        except Exception as e:
                            print_status(f"Episode {ep_num} generated an exception: {str(e)}", "error")
                            failed_downloads += 1
            else:
                for episode_num, url, video_source in zip(episode_numbers, urls, video_sources):
                    success, _ = download_episode(episode_num, url, video_source, anime_name, save_dir, use_ts_threading, automatic_mp4, pre_selected_tool)
                    if not success:
                        failed_downloads += 1

            print_separator()
            if failed_downloads == 0:
                print_status("All downloads completed successfully! Enjoy watching! 🎉", "success")
                input(f"{Colors.BOLD}Press Enter to exit...{Colors.ENDC}")
                return 0
            else:
                print_status(f"Completed with {failed_downloads} failed downloads", "warning")
                input(f"{Colors.BOLD}Press Enter to exit...{Colors.ENDC}")
                return 1

        except KeyboardInterrupt:
            print_status("\n\nProgram interrupted by user", "error")
            return 1
        except Exception as e:
            print_status(f"Unexpected error: {str(e)}", "error")
            return 1
    except Exception as e:
        print_status(f"Fatal error: {str(e)}", "error")
        return 1
if __name__ == "__main__":
    sys.exit(main())