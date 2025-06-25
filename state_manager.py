import os
import json
import logging
from datetime import datetime, timedelta
from typing import Set, Optional

# Původní soubor pro zpětnou kompatibilitu
STATE_FILE = "last_processed.txt"
# Nový soubor s rozšířenou funkcionalitou
STATE_FILE_NEW = "processed_urls.json"

def get_last_processed_file():
    """
    Načte název posledního zpracovaného souboru ze stavového souboru (starý formát).
    
    DEPRECATED: Tato funkce je zachována pro zpětnou kompatibilitu.
    Nové implementace by měly používat get_processed_urls().

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
    Uloží název posledního zpracovaného souboru do stavového souboru (starý formát).
    
    DEPRECATED: Tato funkce je zachována pro zpětnou kompatibilitu.
    Nové implementace by měly používat save_processed_url().

    Args:
        filename (str): Název souboru k uložení.
    """
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            f.write(filename)
        logging.info(f"Nový stav uložen. Poslední zpracovaný soubor: {filename}")
    except IOError as e:
        logging.error(f"Chyba při zápisu do stavového souboru: {e}")

def get_processed_urls() -> Set[str]:
    """
    Načte sadu všech zpracovaných URL z nového stavového souboru.
    
    Pokud nový soubor neexistuje, pokusí se migrovat ze starého formátu.

    Returns:
        Set[str]: Sada URL adres již zpracovaných hlášení.
    """
    # Zkus načíst nový formát
    if os.path.exists(STATE_FILE_NEW):
        try:
            with open(STATE_FILE_NEW, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'processed_urls' in data:
                    # Extrahujeme jen URL z objektů s timestamp
                    urls = {item['url'] for item in data['processed_urls'] if isinstance(item, dict) and 'url' in item}
                    logging.info(f"Načteno {len(urls)} zpracovaných URL z nového formátu.")
                    return urls
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Chyba při čtení nového stavového souboru: {e}")
    
    # Pokud nový soubor neexistuje nebo má chybu, pokus se migrovat ze starého
    if os.path.exists(STATE_FILE):
        logging.info("Migruji ze starého formátu na nový...")
        migrated_urls = migrate_from_old_format(STATE_FILE)
        if migrated_urls:
            # Uložíme migrovaná data do nového formátu
            for url in migrated_urls:
                save_processed_url(url)
            return migrated_urls
    
    logging.info("Žádný stavový soubor nenalezen, začínám s prázdným seznamem.")
    return set()

def save_processed_url(url: str) -> None:
    """
    Uloží nové zpracované URL do stavového souboru.
    
    Pokud URL již existuje, neudělá nic (eliminuje duplikáty).

    Args:
        url (str): URL adresa zpracovaného hlášení.
    """
    # Načteme existující data nebo vytvoříme nová
    data = {"processed_urls": []}
    if os.path.exists(STATE_FILE_NEW):
        try:
            with open(STATE_FILE_NEW, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (IOError, json.JSONDecodeError):
            logging.warning("Nepodařilo se načíst existující data, vytvářím nová.")
    
    # Zkontrolujeme, jestli URL už neexistuje
    if 'processed_urls' in data:
        existing_urls = {item['url'] for item in data['processed_urls'] if isinstance(item, dict) and 'url' in item}
        if url in existing_urls:
            logging.debug(f"URL {url} už je zpracované, přeskakuji.")
            return
    
    # Přidáme nové URL s časovým razítkem
    new_entry = {
        "url": url,
        "processed_at": datetime.now().isoformat()
    }
    data["processed_urls"].append(new_entry)
    
    # Uložíme zpět
    try:
        with open(STATE_FILE_NEW, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Uloženo nové zpracované URL: {url}")
        
        # Pro zpětnou kompatibilitu aktualizujeme i starý soubor
        filename = url.split('/')[-1]  # Extrahujeme název souboru z URL
        save_last_processed_file(filename)
        
    except IOError as e:
        logging.error(f"Chyba při zápisu nového zpracovaného URL: {e}")

def cleanup_old_urls(days: int = 30) -> None:
    """
    Vymaže záznamy starší než zadaný počet dní pro úsporu místa.

    Args:
        days (int): Počet dní, starší záznamy budou smazány. Výchozí je 30 dní.
    """
    if not os.path.exists(STATE_FILE_NEW):
        logging.info("Soubor pro úklid neexistuje.")
        return
    
    try:
        with open(STATE_FILE_NEW, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'processed_urls' not in data:
            return
        
        cutoff_date = datetime.now() - timedelta(days=days)
        original_count = len(data['processed_urls'])
        
        # Filtrujeme pouze záznamy novější než cutoff_date
        filtered_urls = []
        for item in data['processed_urls']:
            if isinstance(item, dict) and 'processed_at' in item:
                try:
                    processed_date = datetime.fromisoformat(item['processed_at'])
                    if processed_date > cutoff_date:
                        filtered_urls.append(item)
                except ValueError:
                    # Pokud se nepodaří parsovat datum, záznam zachováme
                    filtered_urls.append(item)
            else:
                # Starý formát nebo neočekávaná struktura - zachováme
                filtered_urls.append(item)
        
        data['processed_urls'] = filtered_urls
        removed_count = original_count - len(filtered_urls)
        
        if removed_count > 0:
            with open(STATE_FILE_NEW, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info(f"Vymazáno {removed_count} starých záznamů (starších než {days} dní).")
        else:
            logging.info("Žádné staré záznamy k vymazání.")
            
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Chyba při úklidu starých záznamů: {e}")

def migrate_from_old_format(old_file_path: str) -> Set[str]:
    """
    Migruje data ze starého formátu (last_processed.txt) na nový.
    
    Args:
        old_file_path (str): Cesta ke starému souboru.
        
    Returns:
        Set[str]: Sada migrovaných URL.
    """
    try:
        with open(old_file_path, 'r', encoding='utf-8') as f:
            filename = f.read().strip()
        
        if filename:
            # Rekonstruujeme URL z názvu souboru
            url = f"https://rozhlas.milesovice.cz/rozhlas/{filename}"
            logging.info(f"Migrováno ze starého formátu: {url}")
            return {url}
            
    except IOError as e:
        logging.error(f"Chyba při migraci ze starého formátu: {e}")
    
    return set() 