import re
import requests

from src.var import print_status


def fetch_alt_titles(base_url, headers=None):
    """Scrape the English/romaji alternate titles anime-sama shows on an
    anime's catalogue page (element #titreAlter). MAL's own search only
    understands those, not the French title used in anime-sama URLs."""
    match = re.search(r'(https?://[^/]+/catalogue/[^/]+/)', base_url)
    if not match:
        return []
    root_url = match.group(1)

    try:
        response = requests.get(root_url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
    except requests.RequestException as e:
        print_status(f"Could not fetch alternate titles: {str(e)}", "warning")
        return []

    alt_match = re.search(r'id=["\']titreAlter["\'][^>]*>([^<]*)<', html)
    if not alt_match:
        return []

    return [title.strip() for title in alt_match.group(1).split(',') if title.strip()]
