# Tento modul vyžaduje, aby byl v systému nainstalován FFmpeg.
# Pydub ho používá pro konverzi audio formátů.
# Odkaz na stažení: https://ffmpeg.org/download.html

import logging
import os
import requests
from pydub import AudioSegment
from transcriber import transcribe_audio, get_broadcast_datetime
from api_client import send_announcement

OGG_DIR = os.path.join("audio_files", "ogg")
MP3_DIR = os.path.join("audio_files", "mp3")

def download_file(url: str, filename: str) -> str | None:
    """
    Stáhne soubor z dané URL a uloží ho do adresáře pro OGG soubory.

    Args:
        url (str): URL adresa souboru ke stažení.
        filename (str): Název souboru, pod kterým bude uložen.

    Returns:
        str | None: Cesta k uloženému souboru, nebo None v případě chyby.
    """
    ogg_path = os.path.join(OGG_DIR, filename)
    logging.info(f"Stahuji soubor z {url} do {ogg_path}")
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(ogg_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logging.info(f"Soubor '{filename}' byl úspěšně stažen.")
        return ogg_path
    except requests.exceptions.RequestException as e:
        logging.error(f"Chyba při stahování souboru {url}: {e}")
        return None

def convert_ogg_to_mp3(ogg_path: str) -> str | None:
    """
    Konvertuje audio soubor z formátu OGG do MP3.

    Args:
        ogg_path (str): Cesta k OGG souboru.

    Returns:
        str | None: Cesta ke konvertovanému MP3 souboru, nebo None v případě chyby.
    """
    if not os.path.exists(ogg_path):
        logging.error(f"Soubor pro konverzi nenalezen: {ogg_path}")
        return None

    filename = os.path.basename(ogg_path)
    mp3_filename = os.path.splitext(filename)[0] + ".mp3"
    mp3_path = os.path.join(MP3_DIR, mp3_filename)

    logging.info(f"Konvertuji {ogg_path} na {mp3_path}")
    try:
        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(mp3_path, format="mp3")
        logging.info("Konverze na MP3 byla úspěšná.")
        return mp3_path
    except Exception as e:
        logging.error(f"Chyba při konverzi souboru {ogg_path} na MP3: {e}")
        logging.error("Ujistěte se, že máte nainstalovaný a v systémové cestě (PATH) dostupný FFmpeg.")
        return None 

def download_and_process_audio(url: str, filename: str) -> bool:
    """
    Orchestruje celý proces: stažení, konverze, přepis a odeslání.

    Args:
        url (str): URL originálního .ogg souboru.
        filename (str): Název souboru.

    Returns:
        bool: True, pokud vše proběhlo úspěšně, jinak False.
    """
    ogg_path = None
    mp3_path = None
    success = False
    try:
        ogg_path = download_file(url, filename)
        if not ogg_path:
            return False

        mp3_path = convert_ogg_to_mp3(ogg_path)
        if not mp3_path:
            return False

        transcript = transcribe_audio(mp3_path)
        if not transcript:
            return False

        broadcast_date = get_broadcast_datetime(filename)
        if not broadcast_date:
            return False
        
        success = send_announcement(transcript, broadcast_date, url)
        return success

    except Exception as e:
        logging.error(f"Při zpracování souboru {filename} došlo k neočekávané chybě: {e}")
        return False
    finally:
        # Úklid stažených souborů po zpracování
        if ogg_path and os.path.exists(ogg_path):
            os.remove(ogg_path)
            logging.info(f"Smazán dočasný soubor: {ogg_path}")
        if mp3_path and os.path.exists(mp3_path):
            os.remove(mp3_path)
            logging.info(f"Smazán dočasný soubor: {mp3_path}") 