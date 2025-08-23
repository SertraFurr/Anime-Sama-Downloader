import os
import requests
from utils.var import Colors, print_status, print_separator

def print_episodes(episodes):
    print(f"\n{Colors.BOLD}{Colors.HEADER}📺 AVAILABLE EPISODES{Colors.ENDC}")
    print_separator("=")
    
    for category, urls in episodes.items():
        print(f"\n{Colors.BOLD}{Colors.OKCYAN}🎮 {category}:{Colors.ENDC} ({len(urls)} episodes)")
        print_separator("─", 40)
        for i, url in enumerate(urls, start=1):
            url = url.lower()
            if "vk.com" in url or "myvi.tv" in url:
                print(f"{Colors.FAIL}  {i:2d}. Episode {i} - {url[:60]}... ❌ DEPRECATED{Colors.ENDC}")
            elif 'sendvid.com' in url:
                print(f"{Colors.OKGREEN}  {i:2d}. Episode {i} - SendVid ✅{Colors.ENDC}")
            elif 'movearnpre.com' in url:
                print(f"{Colors.OKGREEN}  {i:2d}. Episode {i} - Movearnpre ✅{Colors.ENDC}")
            elif 'video.sibnet.ru' in url:
                print(f"{Colors.OKGREEN}  {i:2d}. Episode {i} - Sibnet ✅{Colors.ENDC}")
            elif 'oneupload.net' in url or 'oneupload.to' in url:
                print(f"{Colors.OKGREEN}  {i:2d}. Episode {i} - OneUpload ✅{Colors.ENDC}")
            elif 'vidmoly.net' in url or 'vidmoly.to' in url:
                print(f"{Colors.OKGREEN}  {i:2d}. Episode {i} - Vidmoly ✅{Colors.ENDC}")
            elif 'smoothpre.com' in url:
                print(f"{Colors.OKGREEN}  {i:2d}. Episode {i} - Smoothpre ✅{Colors.ENDC}")
            else:
                print(f"{Colors.WARNING}  {i:2d}. Episode {i} - Unknown source ⚠️ {Colors.ENDC} {url[:60]}...")

def get_player_choice(episodes):
    print(f"\n{Colors.BOLD}{Colors.HEADER}🎮 SELECT PLAYER{Colors.ENDC}")
    print_separator()
    
    available_players = list(episodes.keys())
    for i, player in enumerate(available_players, 1):
        working_episodes = sum(1 for url in episodes[player] 
                     if 'sendvid.com' in url or 'video.sibnet.ru' in url or 'oneupload.net' in url or 'oneupload.to' in url or 'vidmoly.net' in url or 'vidmoly.to' in url or 'movearnpre.com' in url or 'smoothpre.com' in url or 'Smoothpre.com' in url)
        total_episodes = len(episodes[player])
        print(f"{Colors.OKCYAN}  {i}. {player} ({working_episodes}/{total_episodes} working episodes){Colors.ENDC}")
    
    while True:
        try:
            choice = input(f"\n{Colors.BOLD}Enter player number (1-{len(available_players)}) or type player name: {Colors.ENDC}").strip()
            
            if choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(available_players):
                    return available_players[choice_idx]
                else:
                    print_status(f"Please enter a number between 1 and {len(available_players)}", "error")
            else:
                player_input = choice.lower()
                if player_input.isdigit():
                    player_choice = f"Player {player_input}"
                elif player_input.startswith("player") and player_input[6:].isdigit():
                    player_choice = f"Player {player_input[6:]}"
                elif player_input.replace(" ", "").startswith("player") and player_input.replace(" ", "")[6:].isdigit():
                    player_choice = f"Player {player_input.replace(' ', '')[6:]}"
                else:
                    player_choice = choice.title()
                
                if player_choice in episodes:
                    return player_choice
                else:
                    print_status("Invalid player choice. Try again.", "error")
        except KeyboardInterrupt:
            print_status("\nOperation cancelled by user", "error")
            return None
        except Exception:
            print_status("Invalid input. Please try again.", "error")

def get_episode_choice(episodes, player_choice):
    print(f"\n{Colors.BOLD}{Colors.HEADER}📺 SELECT EPISODE - {player_choice}{Colors.ENDC}")
    print_separator()
    
    num_episodes = len(episodes[player_choice])
    working_episodes = []
    

    for i, url in enumerate(episodes[player_choice], 1):
        url = url.lower()
        if 'sendvid.com' in url or 'video.sibnet.ru' in url or 'oneupload.net' in url or 'oneupload.to' in url or 'vidmoly.net' in url or 'vidmoly.to' in url or 'movearnpre.com' in url or 'smoothpre.com' in url:
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
            
            print(f"{Colors.OKGREEN}  {i:2d}. Episode {i} - {source_type} ✅{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}  {i:2d}. Episode {i} - Deprecated ❌{Colors.ENDC}")
    
    if not working_episodes:
        print_status("No working episodes found for this player!", "error")
        return None
    
    print(f"\n{Colors.OKCYAN}Available episodes: {len(working_episodes)} out of {num_episodes}{Colors.ENDC}")
    
    while True:
        try:
            episode_input = input(f"\n{Colors.BOLD}Enter episode number (1-{num_episodes}): {Colors.ENDC}").strip()
            episode_num = int(episode_input)
            
            if 1 <= episode_num <= num_episodes:
                episode_url = episodes[player_choice][episode_num - 1]
                if 'vk.com' in episode_url or 'myvi.tv' in episode_url:
                    print_status("This episode source is deprecated and cannot be downloaded", "error")
                    continue
                return episode_num - 1
            else:
                print_status(f"Episode number must be between 1 and {num_episodes}", "error")
        except KeyboardInterrupt:
            print_status("\nOperation cancelled by user", "error")
            return None
        except ValueError:
            print_status("Invalid episode number. Please enter a number.", "error")
