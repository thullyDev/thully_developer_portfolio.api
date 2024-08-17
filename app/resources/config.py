from environs import Env

config = Env()
config.read_env()

DB_URL: str = config("DB_URL")
REDIS_URL: str = config("REDIS_URL")
ORIGINS: str = config("ORIGINS")
SITE_KEY: str = config("SITE_KEY")