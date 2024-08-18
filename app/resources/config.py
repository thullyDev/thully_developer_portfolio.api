from environs import Env

config = Env()
config.read_env()

DB_URL: str = config("DB_URL")
REDIS_URL: str = config("REDIS_URL")
ORIGINS: str = config("ORIGINS")
SITE_KEY: str = config("SITE_KEY")
IMAGEKIT_PUBLIC_KEY: str = config("IMAGEKIT_PUBLIC_KEY")
IMAGEKIT_PRIVATE_KEY: str = config("IMAGEKIT_PRIVATE_KEY")
IMAGEKIT_URL_ENDPOINT: str = config("IMAGEKIT_URL_ENDPOINT")