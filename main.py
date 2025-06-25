import logging
import os
from scraper import fetch_announcements
from audio_processor import download_and_process_audio
from state_manager import get_processed_urls, save_processed_url, cleanup_old_urls
from config import LOGGING_LEVEL

# Nastavení logování
logging.basicConfig(level=LOGGING_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Hlavní funkce, která orchestruje stahování, zpracování a odesílání hlášení.
    
    Nová logika podporuje více hlášení za den tím, že si udržuje sadu všech 
    zpracovaných URL místo jen posledního souboru.
    """
    logging.info("Spouštím proces zpracování hlášení rozhlasu.")

    # Vytvoření potřebných adresářů, pokud neexistují
    os.makedirs("audio_files/ogg", exist_ok=True)
    os.makedirs("audio_files/mp3", exist_ok=True)

    try:
        all_urls = fetch_announcements()
        if not all_urls:
            return

        # Načteme sadu všech zpracovaných URL
        processed_urls = get_processed_urls()
        logging.info(f"Celkem máme {len(processed_urls)} zpracovaných URL v historii.")

        # Najdeme nová URL - ta, která ještě nejsou v sadě zpracovaných
        new_urls = [url for url in all_urls if url not in processed_urls]

        if new_urls:
            logging.info(f"Nalezeno {len(new_urls)} nových hlášení k zpracování.")
            for url in new_urls:
                filename = url.split('/')[-1]
                logging.info(f"--- Zpracovávám: {filename} ---")
                try:
                    success = download_and_process_audio(url, filename)
                    if success:
                        save_processed_url(url)
                        logging.info(f"✅ Úspěšně zpracováno a uloženo: {url}")
                    else:
                        logging.error(f"❌ Nepodařilo se zpracovat: {url}")
                except Exception as e:
                    logging.error(f"Při zpracování souboru {filename} došlo k chybě: {e}")
        else:
            logging.info("Nebyly nalezeny žádné nové hlášení k zpracování.")

        # Vyčistíme staré záznamy (starší než 30 dní) pro úsporu místa
        cleanup_old_urls(days=30)

    except Exception as e:
        logging.error(f"Během hlavního procesu nastala kritická chyba: {e}")
        
    logging.info("Proces zpracování hlášení dokončen.")


if __name__ == "__main__":
    main() 