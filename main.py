import logging
import os
from scraper import fetch_announcements
from audio_processor import download_and_process_audio
from state_manager import get_last_processed_file, save_last_processed_file
from config import LOGGING_LEVEL

# Nastavení logování
logging.basicConfig(level=LOGGING_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Hlavní funkce, která orchestruje stahování, zpracování a odesílání hlášení.
    """
    logging.info("Spouštím proces zpracování hlášení rozhlasu.")

    # Vytvoření potřebných adresářů, pokud neexistují
    os.makedirs("audio_files/ogg", exist_ok=True)
    os.makedirs("audio_files/mp3", exist_ok=True)

    try:
        all_urls = fetch_announcements()
        if not all_urls:
            return

        last_processed_filename = get_last_processed_file()

        if last_processed_filename:
            logging.info(f"Poslední zpracovaný soubor byl: {last_processed_filename}")
            try:
                # Najdeme index posledního zpracovaného souboru
                last_processed_url = next(url for url in all_urls if last_processed_filename in url)
                last_index = all_urls.index(last_processed_url)
                # Vezmeme jen novější soubory
                new_urls = all_urls[last_index + 1:]
            except StopIteration:
                # Pokud se poslední zpracovaný soubor už v seznamu nenachází (např. byl smazán ze stránky),
                # zpracujeme pro jistotu vše, jako při prvním spuštění.
                logging.warning(f"Poslední zpracovaný soubor '{last_processed_filename}' nebyl nalezen v aktuálním seznamu. Zpracovávám vše znovu.")
                new_urls = all_urls[-5:] # Zpracujeme 5 nejnovějších
        else:
            logging.info("Stavový soubor 'last_processed.txt' nenalezen, jedná se o první spuštění.")
            # Při prvním spuštění zpracujeme 5 nejnovějších
            new_urls = all_urls[-5:]
            logging.info(f"První spuštění, zpracovávám {len(new_urls)} nejnovějších hlášení.")

        if new_urls:
            logging.info(f"Nalezeno {len(new_urls)} nových hlášení k zpracování.")
            for url in new_urls:
                filename = url.split('/')[-1]
                logging.info(f"--- Zpracovávám: {filename} ---")
                try:
                    success = download_and_process_audio(url, filename)
                    if success:
                        save_last_processed_file(filename)
                except Exception as e:
                    logging.error(f"Při zpracování souboru {filename} došlo k chybě: {e}")
        else:
            logging.info("Nebyly nalezeny žádné nové hlášení k zpracování.")

    except Exception as e:
        logging.error(f"Během hlavního procesu nastala kritická chyba: {e}")
        
    logging.info("Proces zpracování hlášení dokončen.")


if __name__ == "__main__":
    main() 