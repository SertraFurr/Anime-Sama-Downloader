def validate_anime_sama_url(url):
    pattern = re.compile(r'^https://anime-sama\.(?:fr|org)/catalogue/[^/]+/saison\d+[a-zA-Z]*(?:-\d+[a-zA-Z]*)?/(?:vostfr|vf|vo)/?$')
    if pattern.match(url):
        return True, ""
    else:
        return False, (
            "Invalid URL. Format should be:\n"
            "  https://anime-sama.fr/catalogue/<anime-name>/saison<NUMBER>/<language>/\n"
            "Where <language> is VOSTFR, VF, VO, etc. Also .org domain is accepted."
        )