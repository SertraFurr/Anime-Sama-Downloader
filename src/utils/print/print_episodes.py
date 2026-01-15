from src.var import Colors, print_separator

def print_episodes(episodes):
    SOURCE_CONFIG = {
        "vk.com": ("DEPRECATED", Colors.FAIL, False),
        "myvi.tv": ("DEPRECATED", Colors.FAIL, False),
        "oneupload.net": ("DOWN", Colors.FAIL, False),
        "oneupload.to": ("DOWN", Colors.FAIL, False),
        "myvi.top": ("Malicious", Colors.FAIL, False),
        "sendvid.com": ("SendVid", Colors.OKGREEN, True),
        "movearnpre.com": ("Movearnpre", Colors.OKGREEN, True),
        "video.sibnet.ru": ("Sibnet", Colors.OKGREEN, True),
        "vidmoly.net": ("Vidmoly", Colors.OKGREEN, True),
        "vidmoly.to": ("Vidmoly", Colors.OKGREEN, True),
        "smoothpre.com": ("Smoothpre", Colors.OKGREEN, True),
        "mivalyo.com": ("Mivalyo", Colors.OKGREEN, True),
        "dingtezuni.com": ("Dingtezuni", Colors.OKGREEN, True),
        "embed4me.com": ("Embed4me", Colors.OKGREEN, True),
    }

    print(f"\n{Colors.BOLD}{Colors.HEADER}📺 AVAILABLE EPISODES{Colors.ENDC}")
    print_separator("=")
    
    for category, urls in episodes.items():
        print(f"\n{Colors.BOLD}{Colors.OKCYAN}🎮 {category}:{Colors.ENDC} ({len(urls)} episodes)")
        print_separator("─", 40)
        
        for i, url in enumerate(urls, start=1):
            url_lower = url.lower()
            found = False
            
            for domain, (label, color, ok) in SOURCE_CONFIG.items():
                if domain in url_lower:
                    status_symbol = "✅" if ok else "❌"
                    display_label = f"{label} {status_symbol}"
                    suffix = f" - {url[:60]}..." if not ok else ""
                    
                    print(f"{color}  {i:2d}. Episode {i} - {display_label}{suffix}{Colors.ENDC}")
                    found = True
                    break
            
            if not found:
                print(f"{Colors.WARNING}  {i:2d}. Episode {i} - Unknown source ⚠️ {Colors.ENDC} {url[:60]}...")
