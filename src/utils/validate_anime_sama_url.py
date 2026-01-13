import re
from src.var import Colors, get_domain

def validate_anime_sama_url(url):
    pattern = re.compile(
    r'^https?://(?:www\.)?anime-sama\.[^/]+/catalogue/[^/]+/.+/.+/?$', 
    re.IGNORECASE
    )
    if pattern.match(url):
        return True, ""
    else:
        return False, (
            f"{url} Invalid URL. Format should be:\n"
            f"  https://{get_domain()}/catalogue/<anime-name>/<season-type>/<language>/\n"
            f"  https://{get_domain()}/catalogue/<anime-name>/scan/<language>/\n"
        )
