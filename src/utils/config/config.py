import json
import os
import requests
from src.var import Colors, print_status

def get_cookies():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            cf_clearance = config.get('cf_clearance_cookie', '')
            if cf_clearance == "":
                return False
            return cf_clearance
    except FileNotFoundError:
        return False

def set_cookies(cf_clearance_value):
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    config['cf_clearance_cookie'] = cf_clearance_value
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

def check_cookies(domain):

    headers = {
        "Accept": "text/html",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "fr-FR,fr;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Cookie": "cf_clearance=" + get_cookies()
    }
    req = requests.get(f"https://{domain}", headers=headers)
    if req.status_code != 403:
        print_status("Cloudflare cookies are valid.", "success")
        return True