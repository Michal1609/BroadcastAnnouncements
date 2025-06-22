import os
import logging

STATE_FILE = "last_processed.txt"

def get_last_processed_file():
    """
    Načte název posledního zpracovaného souboru ze stavového souboru.

    Returns:
        str | None: Název souboru, nebo None, pokud soubor neexistuje.
    """
    if not os.path.exists(STATE_FILE):
        logging.info("Stavový soubor 'last_processed.txt' nenalezen, jedná se o první spuštění.")
        return None
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            last_file = f.read().strip()
            logging.info(f"Poslední zpracovaný soubor byl: {last_file}")
            return last_file
    except IOError as e:
        logging.error(f"Chyba při čtení stavového souboru: {e}")
        return None

def save_last_processed_file(filename):
    """
    Uloží název posledního zpracovaného souboru do stavového souboru.

    Args:
        filename (str): Název souboru k uložení.
    """
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            f.write(filename)
        logging.info(f"Nový stav uložen. Poslední zpracovaný soubor: {filename}")
    except IOError as e:
        logging.error(f"Chyba při zápisu do stavového souboru: {e}") 