def package_check(ask_install=False, first_run=False):
    missing_packages = []

    try:
        import requests
    except ImportError:
        missing_packages.append("requests")

    try:
        from tqdm import tqdm
    except ImportError:
        missing_packages.append("tqdm")

    try:
        import av
    except ImportError:
        missing_packages.append("av")

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        missing_packages.append("beautifulsoup4")

    if missing_packages and ask_install:
        print("Missing packages:", ", ".join(missing_packages))
        if not first_run:
            for package in missing_packages:
                try:
                    print_status(f"Installing {package}...", "info")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                except subprocess.CalledProcessError:
                    print_status(f"Failed to install {package}.", "error")
                    return False
            missing_packages = []
            try:
                import requests
            except ImportError:
                missing_packages.append("requests")
            try:
                from tqdm import tqdm
            except ImportError:
                missing_packages.append("tqdm")

            try:
                import av
            except ImportError:
                missing_packages.append("av")

            try:
                from bs4 import BeautifulSoup
            except ImportError:
                missing_packages.append("beautifulsoup4")
            
            if missing_packages:
                print_status(f"Some packages still missing after installation: {', '.join(missing_packages)}", "error")
                return False
        else:
            return False
    return len(missing_packages) == 0
