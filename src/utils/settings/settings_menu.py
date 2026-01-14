import os
from src.var import Colors, print_header, print_separator, print_status
from src.utils.config.config import get_setting, set_setting

def settings_menu():
    while True:
        print_header()
        print(f"\n{Colors.BOLD}{Colors.HEADER}⚙️ CONFIGURATION{Colors.ENDC}")
        print_separator()
        
        current_template = get_setting("save_template", "./videos/{anime}/{season}")
        
        print(f"{Colors.OKCYAN}1. Change Save Path Template{Colors.ENDC}")
        print(f"   {Colors.WARNING}Current: {current_template}{Colors.ENDC}")
        print(f"   {Colors.FAIL}Keywords: {{anime}}, {{season}}{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}0. Back to Main Menu{Colors.ENDC}")
        print_separator()
        
        choice = input(f"{Colors.BOLD}Select option: {Colors.ENDC}").strip()
        
        if choice == '1':
            print(f"\n{Colors.BOLD}Enter new save path template:{Colors.ENDC}")
            print(f"You can use keywords {Colors.WARNING}{{anime}}{Colors.ENDC} and {Colors.WARNING}{{season}}{Colors.ENDC} which will be automatically replaced.")
            print(f"You can also remove them if you want a simpler structure.")
            print(f"\n{Colors.BOLD}Examples (for anime 'Roshidere' season 'saison1'):{Colors.ENDC}")
            print(f" - ./videos/{{anime}}/{{season}}   →  ./videos/Roshidere/saison1/")
            print(f" - ./videos/{{anime}}            →  ./videos/Roshidere/")
            print(f" - C:/Downloads/{{season}}       →  C:/Downloads/saison1/")
            print(f" - ./MyAnimeFolder/             →  ./MyAnimeFolder/ (All files in one folder)")
            
            new_template = input(f"{Colors.BOLD}Template: {Colors.ENDC}").strip()
            if new_template:
                set_setting("save_template", new_template)
                print_status("Save path template updated!", "success")
            else:
                print_status("Cancelled.", "warning")
            input("Press Enter to continue...")
            
        elif choice == '0':
            break
        else:
            print_status("Invalid option", "error")
