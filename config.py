import os
import logging
from dotenv import load_dotenv

# Načte proměnné prostředí ze souboru .env (pokud existuje)
# To je užitečné pro lokální vývoj.
load_dotenv()

# URL adresa pro stahování hlášení
BROADCAST_URL = "https://rozhlas.milesovice.cz/rozhlas.php"

# Konfigurace logování
LOGGING_LEVEL = logging.INFO

# Načtení klíčů z proměnných prostředí
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEB_API_KEY = os.getenv("WEB_API_KEY")
WEB_API_ENDPOINT = os.getenv("WEB_API_ENDPOINT")

# Konfigurace pro odesílání na web API
# WEB_API_ENDPOINT = "https://localhost:7075/api/BroadcastAnnouncement/"

# Validace, zda byly klíče načteny
if not GEMINI_API_KEY:
    raise ValueError("Chybí proměnná prostředí GEMINI_API_KEY.")
if not WEB_API_KEY:
    raise ValueError("Chybí proměnná prostředí WEB_API_KEY.")
if not WEB_API_ENDPOINT:
    raise ValueError("Chybí proměnná prostředí WEB_API_ENDPOINT.") 