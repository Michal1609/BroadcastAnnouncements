# Seznam úkolů pro projekt Hlášení Rozhlasu

Tento soubor sleduje postup vývoje.

## Fáze 1: Základní nastavení a scraping [DOKONČENO]

- [x] Inicializace projektu, vytvoření `.gitignore`, `requirements.txt`.
- [x] Vytvoření `config.py` pro ukládání konfiguračních proměnných (URL, API klíče).
- [x] Implementace `scraper.py` pro stahování a parsování HTML stránky.
- [x] Extrakce všech odkazů na `.ogg` soubory.

## Fáze 2: Zpracování audia a správa stavu [DOKONČENO]

- [x] Vytvoření `state_manager.py` pro sledování posledního zpracovaného souboru.
- [x] Implementace logiky, aby se zpracovávala pouze nová hlášení.
- [x] Při prvním spuštění zpracovat 5 nejnovějších hlášení.
- [x] Vytvoření `audio_processor.py`.
- [x] Stažení `.ogg` souboru z URL.
- [x] Konverze staženého `.ogg` souboru na `.mp3` pomocí `pydub`.

## Fáze 3: Přepis a odeslání na API [DOKONČENO]

- [x] Vytvoření `transcriber.py`.
- [x] Extrakce data a času vysílání z názvu souboru.
- [x] Nahrání `.mp3` souboru do Gemini Files API.
- [x] Odeslání požadavku na přepis pomocí `gemini-1.5-flash`.
- [x] Získání textového přepisu.
- [x] Vytvoření `api_client.py`.
- [x] Odeslání finálního přepisu a data vysílání na produkční webové API.
- [x] Zajištění správného formátu (JSON payload, hlavičky, API klíč).

## Fáze 4: Dokončení a nasazení [DOKONČENO]

- [x] Integrace všech modulů do hlavního skriptu `main.py`.
- [x] Přidání robustního logování pro všechny kroky.
- [x] Implementace error handlingu pro případ selhání stahování, konverze nebo API volání.
- [x] Použití proměnných prostředí pro citlivé údaje (`.env`).
- [x] Vytvoření `README.md` s popisem projektu a instrukcemi ke spuštění.
- [x] Vytvoření `deploy.sh` pro automatizované nasazení na Raspberry Pi.
- [x] Nastavení CRON úlohy pro pravidelné spouštění každých 5 minut.
- [x] Úspěšné nasazení a ověření funkčnosti v produkčním prostředí.

## Fáze 5: Další úpravy a vylepšení

- [x] Přidání `audioUrl` do API volání pro odeslání odkazu na původní audio soubor.
- [x] Oprava SSL problémů pro lokální vývoj s self-signed certifikáty.
- [x] Úspěšné otestování kompletního procesu - zpracováno 5 hlášení s novým parametrem `audioUrl`.

## Fáze 6: Bezpečnost a Git repozitář [DOKONČENO]

- [x] Odstranění všech API klíčů z kódu a dokumentace.
- [x] Bezpečné nastavení environment variables přes `.env` soubory.
- [x] Vytvoření `.env.example` jako šablony pro konfiguraci.
- [x] Rozdělení `deploy.sh` na demo verzi (pro Git) a produkční (lokální s klíči).
- [x] Vytvoření kompletní dokumentace v `README.md` s bezpečnostními pokyny.
- [x] Úspěšné nahrání projektu na GitHub: https://github.com/Michal1609/BroadcastAnnouncements.git
- [x] Úspěšné nasazení aktualizované verze na Raspberry Pi 5 v produkčním prostředí.
- [x] Ověření funkčnosti CRON úlohy (každých 5 minut) na produkci.

## Fáze 7: Oprava detekce více hlášení za den [DOKONČENO] ✅

**Problém**: Systém ignoroval další hlášení za den a některá hlášení bez .ogg přípony.
- Původní logika spoléhala na chronologické pořadí v seznamu URL  
- Scraper detekoval pouze soubory s .ogg příponou
- Při více hlášeních za den se zpracovalo jen první

**Implementované řešení**:
- [x] ✅ Změněn `state_manager.py` - místo ukládání posledního souboru ukládá **sadu všech zpracovaných URL**
- [x] ✅ Aktualizován `main.py` - místo hledání indexu porovnává URL přímo proti seznamu zpracovaných
- [x] ✅ Přidána funkce pro mazání starých záznamů (starších než 30 dní)
- [x] ✅ Zachována zpětná kompatibilita s existujícím `last_processed.txt`
- [x] ✅ Opraven `scraper.py` - detekuje hlášení s i bez .ogg přípony (vynechává XML soubory)

**Technické úpravy realizované**:
- [x] ✅ `state_manager.py`: Nové funkce `get_processed_urls()`, `save_processed_url()`, `cleanup_old_urls()`
- [x] ✅ `main.py`: Změna logiky - `new_urls = [url for url in all_urls if url not in processed_urls]`
- [x] ✅ `scraper.py`: Rozšířena detekce - `is_ogg_file or is_announcement_file`
- [x] ✅ Migrace ze starého formátu na nový JSON formát
- [x] ✅ Unit testy pro novou logiku

**Testování dokončeno**:
- [x] ✅ Simulována situace s více hlášeními za den (25.6.1, 25.6.2, 25.6.3, 25.6)
- [x] ✅ Ověřena zpětná kompatibilita s `last_processed.txt`
- [x] ✅ Otestováno na Windows prostředí - vše funguje správně

**Výsledek**: Systém nyní správně zpracovává všechna hlášení za den, včetně různých formátů souborů.

