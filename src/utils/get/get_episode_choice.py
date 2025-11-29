import os
import requests
from utils.var import Colors, print_status, print_separator

def get_episode_choice(episodes, player_choice):
    print(f"\n{Colors.BOLD}{Colors.HEADER}📺 SELECT EPISODE - {player_choice}{Colors.ENDC}")
    print_separator()
    
    num_episodes = len(episodes[player_choice])
    working_episodes = []
    
    for i, url in enumerate(episodes[player_choice], 1):
        url = url.lower()
        url_list = ["dingtezuni.com", "sendvid.com", "video.sibnet.ru", "oneupload.net", "oneupload.to", "vidmoly.net", "vidmoly.to", "movearnpre.com", "smoothpre.com", "mivalyo.com"]
        if any(source in url for source in url_list):
            working_episodes.append(i)
            if 'sendvid.com' in url:
                source_type = "SendVid"
            elif 'video.sibnet.ru' in url:
                source_type = "Sibnet"
            elif 'oneupload.net' in url or 'oneupload.to' in url:
                source_type = "OneUpload"
            elif 'vidmoly.net' in url or 'vidmoly.to' in url:
                source_type = "Vidmoly"
            elif 'movearnpre.com' in url:
                source_type = "Movearnpre"
            elif 'smoothpre.com' in url:
                source_type = "Smoothpre"
            elif 'mivalyo.com' in url:
                source_type = "Mivalyo"
            elif 'dingtezuni.com' in url:
                source_type = "Dingtezuni"
            
            print(f"{Colors.OKGREEN}  {i:2d}. Episode {i} - {source_type} ✅{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}  {i:2d}. Episode {i} - Deprecated ❌{Colors.ENDC}")
    
    if not working_episodes:
        print_status("No working episodes found for this player!", "error")
        return None
    
    print(f"\n{Colors.OKCYAN}Available episodes: {len(working_episodes)} out of {num_episodes}{Colors.ENDC}")
    
    while True:
        try:
            episode_input = input(f"\n{Colors.BOLD}Enter episode number(s) (1-{num_episodes}, comma-separated example 1,2,3, or 'all' for all available): {Colors.ENDC}").strip().lower()
            
            if episode_input == 'all':
                valid_episodes = []
                for i in range(num_episodes):
                    episode_url = episodes[player_choice][i]
                    if not ('vk.com' in episode_url or 'myvi.tv' in episode_url):
                        valid_episodes.append(i)
                if not valid_episodes:
                    print_status("No valid episodes available for download", "error")
                    continue
                return valid_episodes
            
            episode_nums = [int(num.strip()) for num in episode_input.split(',') if num.strip()]
            valid_episodes = []
            for num in episode_nums:
                if 1 <= num <= num_episodes:
                    episode_url = episodes[player_choice][num - 1]
                    if 'vk.com' in episode_url or 'myvi.tv' in episode_url:
                        print_status(f"Episode {num} source is deprecated and cannot be downloaded", "error")
                    else:
                        valid_episodes.append(num - 1)
                else:
                    print_status(f"Episode number {num} is out of range (1-{num_episodes})", "error")
            
            if valid_episodes:
                return valid_episodes
            else:
                print_status("No valid episodes selected", "error")
                
        except KeyboardInterrupt:
            print_status("\nOperation cancelled by user", "error")
            return None
        except ValueError:
            print_status("Invalid input. Please enter numbers (comma-separated) or 'all'.", "error")