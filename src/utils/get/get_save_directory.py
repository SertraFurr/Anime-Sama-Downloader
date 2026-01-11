import os
from src.var import Colors, print_status, print_separator

def get_save_directory(anime_name=None, saison_info=None):
    print(f"\n{Colors.BOLD}{Colors.HEADER}📁 SAVE LOCATION{Colors.ENDC}")
    print_separator()
    
    default_dir = "./videos/"
    if anime_name:
        default_dir += anime_name + "/"
    if saison_info:
        default_dir += saison_info + "/"

    save_dir = input(f"{Colors.OKCYAN}Enter directory to save videos (default: {default_dir}): {Colors.ENDC}").strip()
    
    if not save_dir:
        save_dir = default_dir
    
    try:
        os.makedirs(save_dir, exist_ok=True)
        print_status(f"Save directory set to: {os.path.abspath(save_dir)}", "success")
        return save_dir
    except Exception as e:
        print_status(f"Cannot create directory {save_dir}: {str(e)}", "error")
        print_status(f"Using default directory: {default_dir}", "info")
        os.makedirs(default_dir, exist_ok=True)
        return default_dir
