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

