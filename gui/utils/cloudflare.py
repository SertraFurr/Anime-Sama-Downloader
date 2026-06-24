from gui.utils.config import CloudflareConfig, settings
from var import generate_requests_headers


def get_headers():
    cloudflare_settings: CloudflareConfig = settings.cloudflare_config

    return generate_requests_headers(cloudflare_settings.cf_clearance, cloudflare_settings.user_agent)
