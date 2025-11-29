def extract_anime_name(base_url):
    match = re.search(r'catalogue/([^/]+)/', base_url)
    if match:
        return match.group(1)
    return "episode"