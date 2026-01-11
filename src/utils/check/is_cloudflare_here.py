import requests

def check_if_cloudflare_enabled(domain, headers):
    try:
        response = requests.get(f"https://{domain}/", headers=headers, timeout=10)
        if "https://raw.githubusercontent.com/Anime-Sama/IMG/img/contenu/orb-on-the-movements-of-the-earth.jpg" not in response.text:
            return True
        return False
    except requests.RequestException:
        return False
