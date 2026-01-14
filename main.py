from src.utils.config.config import get_cookies, set_cookies, check_cookies
from src.utils.print.print_status import print_status
from src.var import Colors, get_domain, print_header, print_separator, print_tutorial, generate_requests_headers
from src.utils.check.is_cloudflare_here import check_if_cloudflare_enabled

def tutorial_input():
    print_status("No valid Cloudflare cookies found. Let's set them up!", "info")
    print_status(f"1. Open {get_domain()} in your browser.", "info")
    print_status("2. Press F12 to open Developer Tools.", "info")
    print_status(f"3. Go to the 'Application' tab → Cookies → select {get_domain()}.", "info")
    print_status("4. Copy the value of the 'cf_clearance' cookie.", "info")
    cf_clearance = input("Paste the cf_clearance value here: ").strip()

    print_status("5. In DevTools Console (F12 → Console), run:", "info")
    print_status("   navigator.userAgent", "info")
    print_status("6. Copy the User-Agent string printed in console WITHOUT the ' .", "info")
    user_agent = input("Paste the User-Agent here: ").strip()

    return cf_clearance, user_agent

cloudflare = check_if_cloudflare_enabled(domain=get_domain(), headers={"User-Agent": "Mozilla/5.0"})

if cloudflare:
    cookies_info = get_cookies()
    if cookies_info is False:
        cf_clearance, user_agent = tutorial_input()
        set_cookies(cf_clearance, user_agent)
    cf_clearance, headers = get_cookies()
    request_headers = {"User-Agent": headers.get("User-Agent")}

    while not check_cookies(domain=get_domain(), headers=request_headers):
        print_status("Please update your Cloudflare cookies or use the same User-Agent as before.", "error")
        cf_clearance, user_agent = tutorial_input()
        set_cookies(cf_clearance, user_agent)

    user_agent = headers.get("User-Agent")
    headers = generate_requests_headers(cf_clearance, user_agent)
else:
    headers = generate_requests_headers("None", "Mozilla/5.0")

import os
import sys
import argparse
from concurrent.futures                         import ThreadPoolExecutor, as_completed
from src.utils.fetch.fetch_episodes             import fetch_episodes
from src.utils.fetch.fetch_video_source         import fetch_video_source
from src.utils.print.print_episodes             import print_episodes
from src.utils.get.get_player_choice            import get_player_choice
from src.utils.get.get_episode_choice           import get_episode_choice
from src.utils.check.check_package              import check_package
from src.utils.check.check_ffmpeg_installed     import check_ffmpeg_installed
from src.utils.validate_anime_sama_url          import validate_anime_sama_url
from src.utils.extract.extract_anime_name       import extract_anime_name
from src.utils.get.get_save_directory           import get_save_directory, format_save_path
from src.utils.download.download_episode        import download_episode
from src.utils.search.search_anime              import search_anime
from src.utils.search.expand_catalogue          import expand_catalogue_url
from src.utils.download.download_scan           import download_scan
from src.utils.settings.settings_menu           import settings_menu

# PLEASE DO NOT REMOVE: Original code from https://github.com/sertrafurr/Anime-Sama-Downloader

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--url", default=None)
    parser.add_argument("--search", default=None)
    parser.add_argument("--episodes", default=None)
    parser.add_argument("--player", default=None)
    parser.add_argument("--dest", default=None)
    parser.add_argument("--threads", action='store_true')
    parser.add_argument("--fast", action='store_true')
    parser.add_argument("--mp4", action='store_true')
    parser.add_argument("--tool", default=None)
    parser.add_argument("--no-mal", action='store_true', help="Disable MyAnimeList research")
    parser.add_argument("--latest", action='store_true', help="Download only the latest episode")

    
    args = parser.parse_args()
    interactive = len(sys.argv) == 1

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
        
        base_url = args.url

        if args.search and not base_url:
            results = search_anime(args.search, headers=headers)
            if not results:
                print_status("No results found for search query.", "error")
                return 1
            print(f"\n{Colors.BOLD}{Colors.HEADER}🔍 SEARCH RESULTS{Colors.ENDC}")
            print_separator()
            for i, res in enumerate(results, 1):
                support_text = ""
                if res.get('support') == "Anime Supported":
                    support_text = f" {Colors.OKGREEN}(Anime Supported){Colors.ENDC}"
                elif res.get('support') == "Scans Supported":
                    support_text = f" {Colors.OKGREEN}(Scans Supported){Colors.ENDC}"
                print(f"{Colors.OKCYAN}{i}. {res['title']}{support_text} ({res['url']}){Colors.ENDC}")
            
            while True:
                try:
                    choice = input(f"{Colors.BOLD}Select anime (1-{len(results)}): {Colors.ENDC}").strip()
                    if choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(results):
                            base_url = results[idx]['url']
                            break
                    print_status("Invalid choice", "error")
                except KeyboardInterrupt:
                    return 1



        if not base_url:
            show_tutorial = input(f"{Colors.BOLD}Show tutorial? (y/n, default: n): {Colors.ENDC}").strip().lower()
            if show_tutorial in ['y', 'yes', '1']:
                print_tutorial()
                input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
            
            while True:
                print(f"\n{Colors.BOLD}{Colors.HEADER}🔗 ANIME-SAMA SELECTION{Colors.ENDC}")
                print_separator()
                print(f"{Colors.OKCYAN}1. Paste URL{Colors.ENDC}")
                print(f"{Colors.OKCYAN}2. Search Anime{Colors.ENDC}")
                print(f"{Colors.OKCYAN}3. Settings{Colors.ENDC}")
                mode = input(f"{Colors.BOLD}Choice (1/2/3): {Colors.ENDC}").strip()
                
                if mode == '1':
                    while True:
                        base_url = input(f"{Colors.BOLD}Enter the complete anime-sama URL: {Colors.ENDC}").strip()
                        if not base_url: continue
                        break
                    break
                elif mode == '2':
                    query = input(f"{Colors.BOLD}Enter search query: {Colors.ENDC}").strip()
                    results = search_anime(query, headers=headers)
                    if not results:
                        print_status("No results found.", "error")
                        continue
                    
                    print(f"\n{Colors.BOLD}{Colors.HEADER}🔍 SEARCH RESULTS{Colors.ENDC}")
                    print_separator()
                    for i, res in enumerate(results, 1):
                         support_text = ""
                         if res.get('support') == "Anime Supported":
                             support_text = f" {Colors.OKGREEN}(Anime Supported){Colors.ENDC}"
                         elif res.get('support') == "Scans Supported":
                             support_text = f" {Colors.OKGREEN}(Scans Supported){Colors.ENDC}"
                         elif res.get('support') == "Anime & Scans Supported":
                             support_text = f" {Colors.OKGREEN}(Anime & Scans Supported){Colors.ENDC}"
                         elif res.get('support') == "Unknown":
                             support_text = f" {Colors.FAIL}(Status Unknown){Colors.ENDC}"
                         print(f"{Colors.OKCYAN}{i}. {res['title']}{support_text}{Colors.ENDC}")
                    
                    valid_choice = False
                    while True:
                        choice = input(f"{Colors.BOLD}Select anime (1-{len(results)}) or 'c' to cancel: {Colors.ENDC}").strip()
                        if choice.lower() == 'c': break
                        if choice.isdigit():
                            idx = int(choice) - 1
                            if 0 <= idx < len(results):
                                base_url = results[idx]['url']
                                options = expand_catalogue_url(base_url, headers=headers)
                                if options:
                                    anime_opts = []
                                    scan_opts = []
                                    for opt in options:
                                        if '/scan' in opt['url'].lower():
                                            scan_opts.append(opt)
                                        else:
                                            anime_opts.append(opt)
                                    
                                    options = anime_opts + scan_opts
                                    
                                    print(f"\n{Colors.BOLD}{Colors.HEADER}📅 AVAILABLE SEASONS/VERSIONS{Colors.ENDC}")
                                    print_separator()
                                    
                                    idx_counter = 1
                                    if anime_opts:
                                         print(f"{Colors.BOLD}--- Anime ---{Colors.ENDC}")
                                         for opt in anime_opts:
                                             print(f"{Colors.OKCYAN}{idx_counter}. {opt['name']} ({opt['url']}){Colors.ENDC}")
                                             idx_counter += 1
                                    
                                    if scan_opts:
                                         print(f"{Colors.BOLD}--- Scans ---{Colors.ENDC}")
                                         for opt in scan_opts:
                                             print(f"{Colors.OKBLUE}{idx_counter}. {opt['name']} ({opt['url']}){Colors.ENDC}")
                                             idx_counter += 1
                                    
                                    while True:
                                        s_choice = input(f"{Colors.BOLD}Select season (1-{len(options)}): {Colors.ENDC}").strip()
                                        if s_choice.isdigit():
                                            s_idx = int(s_choice) - 1
                                            if 0 <= s_idx < len(options):
                                                base_url = options[s_idx]['url']
                                                valid_choice = True
                                                break
                                        print_status("Invalid choice", "error")
                                    if valid_choice:
                                        break
                                else:
                                    print_status("This page doesn't seem to contain any anime downloadable content.", "warning")
                                    continue
                    if valid_choice: 
                        break
                elif mode == '3':
                    settings_menu()
                else:
                    print_status("Invalid option", "error")
        
        is_valid, _ = validate_anime_sama_url(base_url)
        if not is_valid:
            print_status("Checking for seasons/versions...", "info")
            season_options = expand_catalogue_url(base_url, headers=headers)
            if season_options:
                anime_opts = []
                scan_opts = []
                for opt in season_options:
                     if '/scan' in opt['url'].lower():
                         scan_opts.append(opt)
                     else:
                         anime_opts.append(opt)
                
                season_options = anime_opts + scan_opts

                print(f"\n{Colors.BOLD}{Colors.HEADER}📅 AVAILABLE SEASONS/VERSIONS{Colors.ENDC}")
                print_separator()

                idx_counter = 1
                if anime_opts:
                        print(f"{Colors.BOLD}--- Anime ---{Colors.ENDC}")
                        for opt in anime_opts:
                            print(f"{Colors.OKCYAN}{idx_counter}. {opt['name']} ({opt['url']}){Colors.ENDC}")
                            idx_counter += 1
                
                if scan_opts:
                        print(f"{Colors.BOLD}--- Scans ---{Colors.ENDC}")
                        for opt in scan_opts:
                            print(f"{Colors.OKBLUE}{idx_counter}. {opt['name']} ({opt['url']}){Colors.ENDC}")
                            idx_counter += 1
                
                while True:
                    choice = input(f"{Colors.BOLD}Select season (1-{len(season_options)}): {Colors.ENDC}").strip()
                    if choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(season_options):
                            base_url = season_options[idx]['url']
                            break
                    print_status("Invalid choice", "error")
            else:
                 print_status("Could not find any seasons/versions. Please define one manually (url/saison...)", "warning")

        is_valid, error_msg = validate_anime_sama_url(base_url)
        if not is_valid:
            print_status(error_msg, "error")
            return 1

        if "/scan" in base_url.lower():
            download_scan(base_url, headers)
            return 0

        anime_name = extract_anime_name(base_url)
        print_status(f"Detected anime: {anime_name}", "info")
        episodes = fetch_episodes(base_url, headers=headers)
        if not episodes:
            print_status("Failed to fetch episodes.", "error")
            return 1
        
        print_episodes(episodes)
        
        player_choice = None
        if args.player:
            avail = list(episodes.keys())
            if args.player in avail:
                player_choice = args.player
            else:
                for p in avail:
                    if args.player.lower() in p.lower():
                        player_choice = p
                        break
                
                if not player_choice:
                    target = args.player.lower()
                    domain_map = {
                        "sibnet": "video.sibnet.ru",
                        "sendvid": "sendvid.com",
                        "vidmoly": ["vidmoly.net", "vidmoly.to"],
                        "oneupload": ["oneupload.net", "oneupload.to"],
                        "movearn": "movearnpre.com",
                        "smooth": "smoothpre.com",
                        "mivalyo": "mivalyo.com",
                        "dingtezuni": "dingtezuni.com",
                        "embed4me": "embed4me.com"
                    }
                    
                    search_domains = []
                    if target in domain_map:
                         val = domain_map[target]
                         if isinstance(val, list): search_domains.extend(val)
                         else: search_domains.append(val)
                    else:
                        search_domains.append(target)
                        
                    for p in avail:
                        urls_to_check = episodes[p][:5] 
                        found_match = False
                        for u in urls_to_check:
                            u_lower = u.lower()
                            if any(d in u_lower for d in search_domains):
                                player_choice = p
                                found_match = True
                                break
                        if found_match:
                            break

            if not player_choice:
                print_status(f"Player '{args.player}' not found.", "error")
                return 1
        else:
            player_choice = get_player_choice(episodes)
        
        if not player_choice:
            return 1
            
        episode_indices = None
        
        if args.latest:
            if episodes and player_choice in episodes:
                count = len(episodes[player_choice])
                if count > 0:
                    episode_indices = [count - 1]
                    print_status(f"Latest episode selected: Episode {count}", "info")
                else:
                    print_status("No episodes found to select latest.", "error")
                    return 1
            else:
                return 1

        if not episode_indices:
            if args.episodes:
                if args.episodes.lower() == 'all':
                    episode_indices = []
                    for i in range(len(episodes[player_choice])):
                        if 'vk.com' not in episodes[player_choice][i] and 'myvi.tv' not in episodes[player_choice][i]:
                            episode_indices.append(i)
                else:
                    try:
                        episode_indices = []
                        for x in args.episodes.split(','):
                            if x.strip():
                                val = int(x.strip())
                                if 1 <= val <= len(episodes[player_choice]):
                                    episode_indices.append(val - 1)
                    except ValueError:
                        print_status("Invalid episode list format", "error")
                        return 1
            else:
                 if not args.latest:
                    episode_indices = get_episode_choice(episodes, player_choice)
            
        if episode_indices is None or not episode_indices:
            return 1

        get_anime_name = extract_anime_name(base_url)
        get_saison_info = base_url.split('/')[-3]

        
        if args.dest:
             save_dir = format_save_path(get_anime_name, get_saison_info, base_path=args.dest)
        elif interactive:
            save_dir = get_save_directory(get_anime_name, get_saison_info)
        else:
            save_dir = format_save_path(get_anime_name, get_saison_info)

        if not args.dest and not interactive:
             os.makedirs(save_dir, exist_ok=True)

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
            print_status("Could not extract video sources", "error")
            return 1
        
        if isinstance(video_sources, str):
            video_sources = [video_sources]
            
        use_threading = args.threads
        use_ts_threading = args.fast
        automatic_mp4 = args.mp4
        pre_selected_tool = args.tool

        if interactive:
            if len(episode_indices) > 1 and not args.threads:
                thread_choice = input(f"{Colors.BOLD}Download all episodes simultaneously? (t/1/y = yes / s = no): {Colors.ENDC}").strip().lower()
                use_threading = thread_choice in ['t', 'threaded', '1', 'y', 'yes']

            if any('m3u8' in src for src in video_sources if src):
                if use_threading:
                    print_status("Using threading with M3U8.", "warning")
                
                if not args.fast:
                     ts_thread_choice = input(f"{Colors.BOLD}Download .ts files simultaneously (fast)? (y/n): {Colors.ENDC}").strip().lower()
                     use_ts_threading = ts_thread_choice in ['t', 'threaded', '1', 'y', 'yes']

                if not args.mp4:
                    auto_mp4_choice = input(f"{Colors.BOLD}Convert to .mp4 automatically? (y/n): {Colors.ENDC}").strip().lower()
                    automatic_mp4 = auto_mp4_choice in ['t', 'threaded', '1', 'y', 'yes']
                    
                    if automatic_mp4:
                        if not pre_selected_tool:
                             while True:
                                t = input(f"{Colors.BOLD}Tool (1=av, 2=ffmpeg): {Colors.ENDC}").strip()
                                if t in ['1', 'av', '']: 
                                    pre_selected_tool = 'av'
                                    break
                                elif t in ['2', 'ffmpeg']:
                                    pre_selected_tool = 'ffmpeg'
                                    break

        failed_downloads = 0
        try:
            if use_threading and len(episode_indices) > 1:
                print_status("Starting threaded downloads...", "info")
                with ThreadPoolExecutor() as executor:
                    future_to_episode = {
                        executor.submit(download_episode, ep_num, url, video_src, get_anime_name, save_dir, use_ts_threading, automatic_mp4, pre_selected_tool, args.no_mal, interactive): ep_num
                        for ep_num, url, video_src in zip(episode_numbers, urls, video_sources)
                    }
                    for future in as_completed(future_to_episode):
                        ep_num = future_to_episode[future]
                        try:
                            success, _ = future.result()
                            if not success: failed_downloads += 1
                        except Exception as e:
                            print_status(f"Error ep {ep_num}: {e}", "error")
                            failed_downloads += 1
            else:
                for episode_num, url, video_source in zip(episode_numbers, urls, video_sources):
                    success, _ = download_episode(episode_num, url, video_source, get_anime_name, save_dir, use_ts_threading, automatic_mp4, pre_selected_tool, args.no_mal, interactive)
                    if not success: failed_downloads += 1

            print_separator()
            if failed_downloads == 0:
                print_status("All downloads completed! 🎉", "success")
                if interactive: input(f"{Colors.BOLD}Press Enter to exit...{Colors.ENDC}")
                return 0
            else:
                print_status(f"Completed with {failed_downloads} failed", "warning")
                if interactive: input(f"{Colors.BOLD}Press Enter to exit...{Colors.ENDC}")
                return 1

        except KeyboardInterrupt:
            print_status("Interrupted", "error")
            return 1
        except Exception as e:
            print_status(f"Error: {e}", "error")
            return 1
    except Exception as e:
        print_status(f"Fatal: {e}", "error")
        return 1

if __name__ == "__main__":
    sys.exit(main())
