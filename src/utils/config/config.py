import json
import os
import requests
from src.var import Colors, print_status

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')


def get_cookies():
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            cf_clearance = config.get('cf_clearance_cookie', '')
            headers = config.get('headers', {})
            if cf_clearance == "" or not headers.get("User-Agent"):
                return False
            return cf_clearance, headers
    except FileNotFoundError:
        return False


def set_cookies(cf_clearance_value, user_agent_value):
    config = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)

    config['cf_clearance_cookie'] = cf_clearance_value
    config['headers'] = {"User-Agent": user_agent_value}

    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)


def check_cookies(domain, headers):
    stored = get_cookies()
    if stored is False:
        print_status("No Cloudflare cookie stored.", "error")
        return False

    cf_clearance_value, stored_headers = stored

    if headers.get("User-Agent") != stored_headers.get("User-Agent"):
        print_status(
            "Headers do not match the User-Agent used when the cookie was set. Please use the same User-Agent.",
            "error"
        )
        return False

    request_headers = headers.copy()
    request_headers['Cookie'] = f'cf_clearance={cf_clearance_value}'

    try:
        req = requests.get(f"https://{domain}", headers=request_headers, timeout=10)
        if req.status_code != 403:
            print_status("Cloudflare cookies are valid.", "success")
            return True
        else:
            print_status("Cloudflare cookies are invalid or expired.", "error")
            return False
    except requests.RequestException as e:
        print_status(f"Request failed: {e}", "error")
        return False
