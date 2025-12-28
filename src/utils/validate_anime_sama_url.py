import re

def validate_anime_sama_url(url):
    pattern = re.compile(
    r'^https?://(?:www\.)?anime-sama\.[^/]+/catalogue/[^/]+/(?:saison\d+(?:-\d+)?|film\d*)/(?:vostfr|vo|vf\d*)/?$', 
    re.IGNORECASE
    )
    if pattern.match(url):
        return True, ""
    else:
        return False, (
            "Invalid URL. Format should be:\n"
            "  https://anime-sama.fr/catalogue/<anime-name>/saison<NUMBER>/<language>/\n"
            "Where <language> is VOSTFR, VF, VO, etc. Also .org domain is accepted."
        )
