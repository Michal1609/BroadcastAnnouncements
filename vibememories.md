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

### Kompletní postup nasazení na Raspberry Pi 5:

#### 1. Příprava lokálního prostředí:
```bash
# Zkopíruj demo deploy script a vyplň API klíče
cp deploy-demo.sh deploy.sh
nano deploy.sh  # Vyplň PROD_GEMINI_API_KEY, PROD_WEB_API_KEY, PROD_WEB_API_ENDPOINT
```

#### 2. Nahrání na Raspberry Pi:
```bash
# Nahrání celého projektu na Pi
scp -r . michal1609@10.0.0.27:/home/michal1609/myapps/BroadcastAnnouncements
```

#### 3. Spuštění deploy scriptu:
```bash
# Připojení a spuštění
ssh michal1609@10.0.0.27
cd /home/michal1609/myapps/BroadcastAnnouncements
chmod +x deploy.sh
./deploy.sh
```

### Co deploy.sh automaticky dělá:
1. **Systémové závislosti**: Instaluje `python3-venv`, `ffmpeg`
2. **Environment**: Vytváří produkční `.env` soubor s API klíči
3. **Python prostředí**: Nastavuje virtuální prostředí `.venv` a instaluje dependencies
4. **CRON úloha**: Konfiguruje automatické spouštění každých 5 minut
5. **Test**: Spustí aplikaci jednou pro ověření funkčnosti

### CRON konfigurace:
```bash
*/5 * * * * cd /home/michal1609/myapps/BroadcastAnnouncements && /home/michal1609/myapps/BroadcastAnnouncements/.venv/bin/python /home/michal1609/myapps/BroadcastAnnouncements/main.py >> cron.log 2>&1 # BroadcastAnnouncements Cron Job
```

### Monitoring produkce:
```bash
# Kontrola CRON úlohy
crontab -l

# Sledování logů
tail -f /home/michal1609/myapps/BroadcastAnnouncements/cron.log

# Kontrola stavu
cd /home/michal1609/myapps/BroadcastAnnouncements
cat last_processed.txt
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
- ✅ **BEZPEČNOST**: Všechny API klíče odstraněny z kódu, používají se environment variables
- ✅ **GIT REPOZITÁŘ**: Projekt nahrán na GitHub s bezpečnou konfigurací
- ✅ **PRODUKČNÍ NASAZENÍ**: Úspěšně nasazeno na Raspberry Pi 5 (22.6.2025)

**Poslední úspěšné nasazení**: 22.6.2025 - projekt bezpečně nahrán na GitHub a nasazen na produkci

## 🔒 Bezpečnostní postupy pro Git a nasazení

### Před nahráním na Git:
1. ✅ **Odstranění API klíčů**: Všechny citlivé údaje odstraněny z kódu
2. ✅ **Environment variables**: Používání `.env` souborů (v `.gitignore`)
3. ✅ **Deploy scripty**: Produkční `deploy.sh` s klíči v `.gitignore`, demo verze `deploy-demo.sh` v Git
4. ✅ **Dokumentace**: `.env.example` jako šablona, `README.md` s bezpečnostními pokyny

### Postup pro nové nasazení:
```bash
# 1. Klonování z Git
git clone https://github.com/Michal1609/BroadcastAnnouncements.git
cd BroadcastAnnouncements

# 2. Příprava konfigurace
cp .env.example .env
nano .env  # Vyplň API klíče

# 3. Příprava deploy scriptu
cp deploy-demo.sh deploy.sh
nano deploy.sh  # Vyplň produkční API klíče

# 4. Nasazení na produkci
scp -r . user@server:/path/to/app
ssh user@server "cd /path/to/app && chmod +x deploy.sh && ./deploy.sh"
```

### Kontrolní checklist před commitem:
- [ ] Žádné API klíče v kódu
- [ ] `.env` soubory v `.gitignore`
- [ ] Produkční `deploy.sh` v `.gitignore`
- [ ] Aktualizovaná dokumentace
- [ ] Funkční demo verze souborů 