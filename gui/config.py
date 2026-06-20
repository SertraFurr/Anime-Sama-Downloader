import atexit

from pydantic import BaseModel


class CloudflareConfig(BaseModel):
    cf_clearance: str
    user_agent: str


class Config(BaseModel):
    cloudflare_config: CloudflareConfig
    domain: str

    def save(self, _, __, ___):
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))

def _load_config(path: str) -> Config:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return Config.model_validate_json(f.read())
    except FileNotFoundError:
        return Config(
            cloudflare_config=CloudflareConfig(
                cf_clearance="None",
                user_agent="Mozilla/5.0"
            ),
            domain="anime-sama.to"
        )


config_path = "config.json"
settings: Config = _load_config(config_path)

atexit.register(settings.save, None, None, None)
