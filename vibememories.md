# Vibe Memories - BroadcastAnnouncements Project

## 🎯 Cíl projektu
Automatický systém pro stahování, zpracování a přepis hlášení rozhlasu z obce Milešovice. Systém každých 5 minut kontroluje nová hlášení, stahuje je, přepisuje pomocí AI a odesílá na webové API pro zobrazení na webu.

## 🏗️ Architektura systému

### Hlavní moduly:
1. **main.py** - Orchestrátor celého procesu
2. **scraper.py** - Stahování a parsování HTML stránky pro nalezení OGG souborů
3. **audio_processor.py** - Stažení OGG → konverze na MP3 → orchestrace celého procesu
4. **transcriber.py** - Komunikace s Gemini AI pro přepis audio na text
5. **api_client.py** - Odeslání výsledků na webové API
6. **state_manager.py** - Sledování posledního zpracovaného souboru
7. **config.py** - Konfigurace a načítání proměnných prostředí

### Flow zpracování:
```
1. scraper.py → Nalezne všechny OGG odkazy na rozhlas.milesovice.cz
2. state_manager.py → Zkontroluje, které soubory už byly zpracovány
3. audio_processor.py → Pro každý nový soubor:
   a) Stáhne OGG soubor
   b) Konvertuje na MP3 (pomocí pydub + FFmpeg)
   c) Zavolá transcriber.py pro přepis
   d) Zavolá api_client.py pro odeslání
   e) Smaže dočasné soubory
4. state_manager.py → Uloží stav posledního zpracovaného souboru
```

## 🌍 Prostředí

### Testovací prostředí (Windows 11):
- **OS**: Windows 11
- **Python**: 3.13.3
- **API Endpoint**: `https://localhost:7075/api/BroadcastAnnouncement/`
- **API Key**: `[NASTAVENO V .env SOUBORU]`
- **SSL**: Self-signed certifikát → `verify=False` v requests
- **Gemini API Key**: `[NASTAVENO V .env SOUBORU]`

### Produkční prostředí (Raspberry Pi 5):
- **OS**: Raspberry Pi OS (Linux)
- **Python**: 3.x (virtuální prostředí `.venv`)
- **API Endpoint**: `https://www.grznar.eu/api/BroadcastAnnouncement/`
- **API Key**: `[NASTAVENO V .env SOUBORU]`
- **SSL**: Produkční certifikát → `verify=True`
- **Cron**: Spouští se každých 5 minut
- **Logy**: `cron.log`

## 🚀 Nasazení na produkci

### Použití deploy.sh scriptu:
```bash
# Na Raspberry Pi 5:
./deploy.sh
```

### Co deploy.sh dělá:
1. Instaluje systémové závislosti (python3-venv, ffmpeg)
2. Vytváří produkční `.env` soubor s produkčními API klíči
3. Nastavuje Python virtuální prostředí a instaluje requirements.txt
4. Konfiguruje CRON úlohu (každých 5 minut)
5. Spustí testovací běh pro ověření funkčnosti

### CRON konfigurace:
```bash
*/5 * * * * cd /path/to/project && .venv/bin/python main.py >> cron.log 2>&1
```

## 🔧 Technické detaily

### Klíčové závislosti:
- **pydub** - Konverze audio formátů (OGG → MP3)
- **audioop-lts** - Náhrada za odstraněný audioop modul v Python 3.13
- **google-generativeai** - Komunikace s Gemini AI (verze 0.8.5+)
- **requests** - HTTP komunikace
- **beautifulsoup4** - HTML parsing
- **python-dotenv** - Načítání .env souborů

### Důležité API parametry:
```json
{
    "Content": "Přepsaný text hlášení",
    "broadcastDateTime": "2025-06-22T12:00:00Z",
    "audioUrl": "https://rozhlas.milesovice.cz/rozhlas/Hlášení XX.X..ogg"
}
```

### Struktura souborů:
```
BroadcastAnnouncements/
├── main.py                 # Hlavní orchestrátor
├── scraper.py             # HTML parsing
├── audio_processor.py     # Audio zpracování + orchestrace
├── transcriber.py         # Gemini AI komunikace
├── api_client.py          # Web API komunikace
├── state_manager.py       # Stav zpracování
├── config.py              # Konfigurace
├── requirements.txt       # Python závislosti
├── deploy.sh              # Produkční nasazení
├── .env                   # Proměnné prostředí
├── .gitignore            # Git ignorované soubory
├── last_processed.txt     # Stav posledního zpracovaného souboru
├── task.md               # Seznam úkolů
├── vibememories.md       # Tato dokumentace
└── audio_files/          # Dočasné audio soubory
    ├── ogg/              # Stažené OGG soubory
    └── mp3/              # Konvertované MP3 soubory
```

## 🐛 Známé problémy a řešení

### Python 3.13 kompatibilita:
- **Problém**: Odstraněný `audioop` modul
- **Řešení**: `pip install audioop-lts`

### SSL certifikáty:
- **Testovací**: `verify=False` pro self-signed certifikáty
- **Produkční**: `verify=True` pro validní certifikáty

### Gemini API:
- **Starší verze**: Chybí `upload_file` funkce
- **Řešení**: `pip install --upgrade google-generativeai`

## 📋 Checklist pro práci s projektem

### Při spuštění na Windows (test):
1. Ověř `.env` soubor s testovacími klíči
2. Zkontroluj, že běží lokální API na portu 7075
3. Spusť: `python main.py`

### Při nasazení na Raspberry Pi:
1. Zkopíruj soubory na Pi
2. Spusť: `./deploy.sh`
3. Zkontroluj logy: `tail -f cron.log`
4. Ověř CRON: `crontab -l`

### Při debugování:
1. Zkontroluj logy v `cron.log` (produkce)
2. Ověř stav v `last_processed.txt`
3. Zkontroluj dostupnost zdrojové stránky
4. Ověř API klíče a endpointy

## 🎵 Aktuální stav
- ✅ Projekt je plně funkční na Windows 11 i Raspberry Pi 5
- ✅ Automatické zpracování každých 5 minut v produkci
- ✅ Přidán parametr `audioUrl` pro odkazy na původní audio
- ✅ Kompatibilita s Python 3.13
- ✅ Robustní error handling a logování
- ✅ SSL konfigurace pro test i produkci

**Poslední úspěšný test**: 22.6.2025 - zpracováno 5 hlášení s novým audioUrl parametrem 