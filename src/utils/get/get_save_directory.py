import os
import re
from src.var import Colors, print_status, print_separator
from src.utils.config.config import get_setting

def sanitize_path(path):
    return re.sub(r'[<>:"|?*]', '', path)

def format_save_path(anime_name, saison_info, base_path=None):
    template = get_setting("save_template", "./videos/{anime}/{season}")
    
    fmt_args = {
        "anime": anime_name if anime_name else "Unknown_Anime",
        "season": saison_info if saison_info else "Unknown_Season"
    }

    if base_path:
        return os.path.join(base_path, fmt_args["anime"], fmt_args["season"])

    try:
        formatted_path = template.format(**fmt_args)
        return os.path.normpath(formatted_path)
    except Exception:
        return os.path.join("./videos", fmt_args["anime"], fmt_args["season"])

def get_save_directory(anime_name=None, saison_info=None):
    formatted_path = format_save_path(anime_name, saison_info)
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}📁 SAVE LOCATION{Colors.ENDC}")
    print_separator()

    print(f"{Colors.OKCYAN}Current save path (from config): {Colors.ENDC}{formatted_path}")
    
    change = input(f"{Colors.BOLD}Press Enter to confirm or type new absolute path: {Colors.ENDC}").strip()
    
    if change:
        save_dir = change
    else:
        save_dir = formatted_path
    
    try:
        os.makedirs(save_dir, exist_ok=True)
        print_status(f"Save directory confirmed: {os.path.abspath(save_dir)}", "success")
        return save_dir
    except Exception as e:
        print_status(f"Cannot create directory {save_dir}: {str(e)}", "error")
        default_fallback = "./videos/"
        print_status(f"Using fallback: {default_fallback}", "info")
        os.makedirs(default_fallback, exist_ok=True)
        return default_fallback
