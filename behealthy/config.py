from environs import Env

ENVIRONMENT: str = Env().str("ENVIRONMENT", "dev")
URL_BASE: str = f"https://{ENVIRONMENT}.sensynehealth.com"
