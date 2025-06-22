import logging
import re
from datetime import datetime
import google.generativeai as genai
from config import GEMINI_API_KEY

# Konfigurace Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def get_broadcast_datetime(filename: str) -> datetime | None:
    """
    Extrahuje datum a čas vysílání z názvu souboru.
    Předpokládá formát 'Hlášení DD.M..ogg'.

    Args:
        filename (str): Název souboru.

    Returns:
        datetime | None: Objekt datetime, nebo None při neúspěchu.
    """
    # Regex pro nalezení DD.M. v názvu souboru
    match = re.search(r'(\d{1,2})\.(\d{1,2})\.', filename)
    if not match:
        logging.error(f"Nepodařilo se extrahovat datum z názvu souboru: {filename}")
        return None
    
    day, month = map(int, match.groups())
    current_year = datetime.now().year
    
    try:
        # Vytvoříme datetime objekt. Čas nastavíme na poledne (12:00).
        return datetime(current_year, month, day, 12, 0)
    except ValueError:
        logging.error(f"Nalezeno neplatné datum: den={day}, měsíc={month}, rok={current_year}")
        return None

def transcribe_audio(mp3_path: str) -> str | None:
    """
    Nahraje MP3 soubor do Gemini a provede přepis na text.

    Args:
        mp3_path (str): Cesta k MP3 souboru.

    Returns:
        str | None: Přepsaný text, nebo None v případě chyby.
    """
    logging.info(f"Nahrávám soubor '{mp3_path}' pro přepis do Gemini...")
    try:
        # Nahrání souboru do Files API Gemini
        audio_file = genai.upload_file(path=mp3_path, display_name=mp3_path)
        logging.info(f"Soubor úspěšně nahrán: {audio_file.uri}")

        # Vytvoření instance modelu a odeslání požadavku na přepis
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        prompt = "prosím, proved přesný přepis tohoto audio souboru, děkuji"
        
        response = model.generate_content([prompt, audio_file])
        
        # Uvolnění souboru z Gemini po zpracování
        genai.delete_file(audio_file.name)
        logging.info(f"Dočasný soubor '{audio_file.display_name}' byl smazán z Gemini.")

        if response and response.text:
            logging.info("Přepis byl úspěšně získán.")
            return response.text.strip()
        else:
            logging.error("Přepis selhal, odpověď z API neobsahuje text.")
            return None

    except Exception as e:
        logging.error(f"Došlo k chybě při komunikaci s Gemini API: {e}")
        return None 