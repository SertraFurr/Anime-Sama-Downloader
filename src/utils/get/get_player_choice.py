import os
import requests
from utils.var import Colors, print_status, print_separator

def get_player_choice(episodes):
    print(f"\n{Colors.BOLD}{Colors.HEADER}🎮 SELECT PLAYER{Colors.ENDC}")
    print_separator()
    
    available_players = list(episodes.keys())
    for i, player in enumerate(available_players, 1):
        working_episodes = sum(1 for url in episodes[player] 
                     if 'sendvid.com' in url or 'dingtezuni.com' in url or  'video.sibnet.ru' in url or 'oneupload.net' in url or 'oneupload.to' in url or 'vidmoly.net' in url or 'vidmoly.to' in url or 'movearnpre.com' in url or 'smoothpre.com' in url or 'Smoothpre.com' in url or 'mivalyo.com' in url)
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
