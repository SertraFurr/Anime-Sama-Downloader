import re
import json
import requests

from src.var import print_status


def _fetch_nakanime_alt_titles(base_url, headers=None):
    match = re.search(r'(https?://[^/]+/anime/\d+/[^/]+)', base_url)
    root_url = match.group(1) if match else base_url

    try:
        response = requests.get(root_url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
    except requests.RequestException as e:
        print_status(f"Could not fetch alternate titles: {str(e)}", "warning")
        return []

    for ld_match in re.finditer(r'<script type=["\']application/ld\+json["\']>(.*?)</script>', html, re.DOTALL):
        try:
            data = json.loads(ld_match.group(1))
        except json.JSONDecodeError:
            continue

        if data.get('@type') != 'TVSeries':
            continue

        names = []
        for key in ("name", "alternateName"):
            value = data.get(key)
            if value and value.strip() and value.strip() not in names:
                names.append(value.strip())
        return names

    return []


def fetch_alt_titles(base_url, headers=None):
    if 'nakanime.tv' in base_url.lower() or 'nakanime.fr' in base_url.lower():
        return _fetch_nakanime_alt_titles(base_url, headers=headers)

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
