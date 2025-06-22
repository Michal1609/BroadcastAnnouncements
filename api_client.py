import logging
import requests
from datetime import datetime
from config import WEB_API_ENDPOINT, WEB_API_KEY
import urllib3

# Potlačení SSL varování pro lokální vývoj
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def send_announcement(content: str, broadcast_date: datetime, audio_url: str) -> bool:
    """
    Odešle přepis hlášení na webové API.

    Args:
        content (str): Přepsaný text hlášení.
        broadcast_date (datetime): Datum a čas vysílání.
        audio_url (str): URL původního audio souboru.

    Returns:
        bool: True, pokud byl požadavek úspěšný, jinak False.
    """
    headers = {
        "x-api-key": WEB_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Převedeme datetime na ISO 8601 formát, který očekává API
    payload = {
        "Content": content,
        "broadcastDateTime": broadcast_date.isoformat() + "Z", # Přidání 'Z' pro UTC
        "audioUrl": audio_url
    }
    
    logging.info(f"Odesílám přepis na {WEB_API_ENDPOINT}")
    try:
        # Pro lokální vývoj s self-signed certifikáty vypneme SSL verifikaci
        response = requests.post(WEB_API_ENDPOINT, json=payload, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        logging.info("Přepis byl úspěšně odeslán na webové API.")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Nepodařilo se odeslat přepis na webové API: {e}")
        # V případě chyby je dobré zalogovat i tělo odpovědi, pokud existuje
        if e.response is not None:
            logging.error(f"Odpověď serveru: {e.response.status_code} - {e.response.text}")
        return False 