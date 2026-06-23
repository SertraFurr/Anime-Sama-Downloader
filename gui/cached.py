from cachetools import cached, TTLCache

from gui.cloudflare import get_headers
from utils.fetch.planning import fetch_planning

planning_cache = TTLCache(maxsize=1, ttl=3600)

@cached(planning_cache)
def get_cached_planning():
    return fetch_planning(get_headers())
