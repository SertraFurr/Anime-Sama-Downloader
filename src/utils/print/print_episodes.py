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
            elif 'mivalyo.com' in url:
                print(f"{Colors.OKGREEN}  {i:2d}. Episode {i} - Mivalyo ✅{Colors.ENDC}")
            elif 'dingtezuni.com' in url:
                print(f"{Colors.OKGREEN}  {i:2d}. Episode {i} - Dingtezuni ✅{Colors.ENDC}")
            else:
                print(f"{Colors.WARNING}  {i:2d}. Episode {i} - Unknown source ⚠️ {Colors.ENDC} {url[:60]}...")