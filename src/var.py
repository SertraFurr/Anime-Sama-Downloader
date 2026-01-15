import random

class SourceDomains:
    _SOURCES = {
        "sendvid": ("SendVid", ["sendvid.com"]),
        "dingtezuni": ("Dingtezuni", ["dingtezuni.com"]),
        "sibnet": ("Sibnet", ["video.sibnet.ru"]),
        "oneupload": ("OneUpload", ["oneupload.net", "oneupload.to"]),
        "vidmoly": ("Vidmoly", ["vidmoly.net", "vidmoly.to"]),
        "movearn": ("Movearnpre", ["movearnpre.com", "ovaltinecdn.com"]),
        "mivalyo": ("Mivalyo", ["mivalyo.com"]),
        "smooth": ("Smoothpre", ["smoothpre.com", "Smoothpre.com"]),
        "embed4me": ("Embed4me", ["embed4me.com", "embed4me"]),
    }

    ONEUPLOAD = _SOURCES["oneupload"][1]
    VIDMOLY = _SOURCES["vidmoly"][1]
    MOVARNPRE = _SOURCES["movearn"][1]

    PLAYERS = [d for _, domains in _SOURCES.values() for d in domains]
    
    DISPLAY_NAMES = {d: name for name, domains in _SOURCES.values() for d in domains}
    
    DOMAIN_MAP = {
        k: (val[1] if len(val[1]) > 1 else val[1][0])
        for k, val in _SOURCES.items()
    }

def get_domain():
    return "anime-sama.si"

def generate_requests_headers(cf_clearance, user_agent=None):
    cookies = f"cf_clearance={cf_clearance}"

    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.8",
        "Referer": "https://anime-sama.si/",
        "Origin": "https://anime-sama.si",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Cookie": cookies,
    }
    return headers

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    header = f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                 ANIME-SAMA VIDEO DOWNLOADER                  ║
╚══════════════════════════════════════════════════════════════╝
{Colors.ENDC}
{Colors.OKCYAN}📺 Download anime episodes from anime-sama.fr easily!{Colors.ENDC}
"""
    print(header)

def print_tutorial():
    tutorial = f"""
{Colors.BOLD}{Colors.HEADER}🎓 COMPLETE TUTORIAL - HOW TO USE{Colors.ENDC}
{Colors.BOLD}{'='*65}{Colors.ENDC}

{Colors.OKGREEN}{Colors.BOLD}Step 1: Find Your Anime on Anime-Sama{Colors.ENDC}
├─ 🌐 Visit: {Colors.OKCYAN}https://anime-sama.fr/catalogue/{Colors.ENDC}
├─ 🔍 Search for your desired anime (e.g., "Roshidere")
├─ 📺 Click on the anime title to view seasons
└─ 📂 Navigate to your preferred season and language

{Colors.OKGREEN}{Colors.BOLD}Step 2: Get the Complete URL{Colors.ENDC}
├─ 🎯 Choose your preferred option:
│   ├─ Season (saison1, saison2, etc.)
│   └─ Language (vostfr, vf, etc.)
├─ 📋 Copy the FULL URL from browser address bar
└─ ✅ Example URL format:
    {Colors.OKCYAN}https://anime-sama.fr/catalogue/roshidere/saison1/vostfr/{Colors.ENDC}

{Colors.OKGREEN}{Colors.BOLD}Step 3: Run This Program{Colors.ENDC}
├─ 🚀 Start the downloader
├─ 📝 Paste the complete URL when prompted
├─ ⚡ Program will automatically fetch available episodes
└─ 🎮 Follow the interactive prompts

{Colors.WARNING}{Colors.BOLD}📌 IMPORTANT NOTES:{Colors.ENDC}
├─ ✅ Supported sources: See inside of the github README
├─ ❌ Other sources are not supported (see GitHub for details)
├─ 🔗 URL must be the complete path including season/language
└─ 📁 Videos save to ./videos/ by default (customizable)

{Colors.OKGREEN}{Colors.BOLD}🎯 Example URLs that work:{Colors.ENDC}
├─ https://anime-sama.fr/catalogue/roshidere/saison1/vostfr/
├─ https://anime-sama.fr/catalogue/demon-slayer/saison1/vf/
├─ https://anime-sama.fr/catalogue/attack-on-titan/saison3/vostfr/
├─ https://anime-sama.fr/catalogue/one-piece/saison1/vostfr/

{Colors.BOLD}{'='*65}{Colors.ENDC}
"""
    print(tutorial)

def print_separator(char="─", length=65):
    print(f"{Colors.OKBLUE}{char * length}{Colors.ENDC}")

def print_status(message, status_type="info"):
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "loading": "⏳"
    }
    colors = {
        "info": Colors.OKBLUE,
        "success": Colors.OKGREEN,
        "warning": Colors.WARNING,
        "error": Colors.FAIL,
        "loading": Colors.OKCYAN
    }
    
    icon = icons.get(status_type, "ℹ️")
    color = colors.get(status_type, Colors.OKBLUE)
    print(f"{color}{icon} {message}{Colors.ENDC}")
