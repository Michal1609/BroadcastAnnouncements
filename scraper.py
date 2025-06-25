import requests
from bs4 import BeautifulSoup
import logging
import os

from config import BROADCAST_URL

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_announcements():
    """
    Stáhne a naparsuje stránku s hlášeními a extrahuje odkazy na audio soubory.

    Returns:
        list: Seznam URL adres k .ogg souborům hlášení.
              Vrací prázdný seznam v případě chyby.
    """
    logging.info(f"Stahuji hlášení z: {BROADCAST_URL}")
    try:
        response = requests.get(BROADCAST_URL, timeout=10)
        response.raise_for_status()  # Vyvolá chybu pro status kódy 4xx/5xx
    except requests.exceptions.RequestException as e:
        logging.error(f"Nepodařilo se stáhnout stránku: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    
    links = []
    for link_tag in soup.find_all('a', href=True):
        href = link_tag['href']
        if not href.startswith('rozhlas/Hlášení'):
            continue
        if href.endswith('.xml'):
            continue
        print(f"DEBUG: href={href}")
        full_url = f"https://rozhlas.milesovice.cz/{href}"
        links.append(full_url)
        logging.debug(f"Nalezen audio soubor: {href}")

    # Stránka řadí soubory od nejnovějšího, ale my je chceme zpracovávat od nejstaršího
    # proto seznam otočíme.
    links.reverse()
    
    if not links:
        logging.warning("Nebyly nalezeny žádné odkazy na .ogg soubory.")
    else:
        logging.info(f"Nalezeno {len(links)} odkazů na hlášení.")
        
    return links

if __name__ == '__main__':
    # Testovací spuštění
    announcement_urls = fetch_announcements()
    if announcement_urls:
        print("Nalezené URL adresy:")
        for url in announcement_urls:
            print(url)
    else:
        print("Nepodařilo se načíst žádné URL adresy.") 