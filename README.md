# BroadcastAnnouncements

Automatický systém pro zpracování hlášení rozhlasu z obce Milešovice. Systém stahuje OGG audio soubory, konvertuje je na MP3, přepisuje pomocí Gemini AI a odesílá na webové API.

## 🔒 Bezpečnost - DŮLEŽITÉ!

**NIKDY necommitujte API klíče do Git repozitáře!**

Všechny citlivé údaje jsou načítány z environment variables nebo `.env` souboru, který je v `.gitignore`.

## 🚀 Rychlé spuštění

### 1. Klonování repozitáře
```bash
git clone https://github.com/Michal1609/BroadcastAnnouncements.git
cd BroadcastAnnouncements
```

### 2. Nastavení environment variables
```bash
# Zkopírujte šablonu
cp .env.example .env

# Editujte .env soubor a vyplňte skutečné API klíče
nano .env
```

### 3. Instalace závislostí
```bash
pip install -r requirements.txt
```

### 4. Spuštění
```bash
python main.py
```

## 🔧 Konfigurace

### API klíče
Potřebujete následující API klíče:

1. **GEMINI_API_KEY**: Získejte na [Google AI Studio](https://aistudio.google.com/app/apikey)
2. **WEB_API_KEY**: API klíč pro vaše webové API
3. **WEB_API_ENDPOINT**: URL endpoint vašeho webového API

### Lokální vývoj vs. Produkce

**Lokální vývoj:**
```env
WEB_API_ENDPOINT=https://localhost:7075/api/BroadcastAnnouncement/
```

**Produkce:**
```env
WEB_API_ENDPOINT=https://www.grznar.eu/api/BroadcastAnnouncement/
```

## 🐧 Nasazení na produkci (Raspberry Pi)

### Příprava environment variables
```bash
export PROD_GEMINI_API_KEY="your_actual_gemini_key"
export PROD_WEB_API_KEY="your_actual_web_api_key"  
export PROD_WEB_API_ENDPOINT="https://www.grznar.eu/api/BroadcastAnnouncement/"
```

### Příprava deploy scriptu
```bash
# Zkopírujte demo verzi a upravte s vašimi klíči
cp deploy-demo.sh deploy.sh
nano deploy.sh  # Vyplňte skutečné API klíče

# Spuštění
chmod +x deploy.sh
./deploy.sh
```

Deploy script automaticky:
- Nainstaluje systémové závislosti (ffmpeg)
- Vytvoří virtuální prostředí
- Nainstaluje Python závislosti
- Nastaví CRON úlohu (každých 5 minut)
- Vytvoří produkční `.env` soubor

## 📁 Struktura projektu

```
BroadcastAnnouncements/
├── main.py              # Hlavní orchestrátor
├── scraper.py           # Stahování a parsování HTML
├── audio_processor.py   # Stahování a konverze audio
├── transcriber.py       # Přepis pomocí Gemini AI
├── api_client.py        # Odesílání na webové API
├── state_manager.py     # Správa stavu zpracování
├── config.py            # Konfigurace a načítání env vars
├── requirements.txt     # Python závislosti
├── deploy-demo.sh      # Demo deploy script (bez API klíčů)
├── deploy.sh           # Skutečný deploy script (v .gitignore)
├── .env.example        # Šablona pro environment variables
└── .gitignore          # Git ignore pravidla
```

## 🔄 Jak to funguje

1. **Scraping**: Stáhne HTML stránku z `https://rozhlas.milesovice.cz/rozhlas.php`
2. **Parsing**: Extrahuje odkazy na `.ogg` audio soubory
3. **State Management**: Zpracovává pouze nová hlášení (sleduje poslední zpracovaný)
4. **Audio Processing**: Stáhne OGG → konvertuje na MP3
5. **Transcription**: Nahraje MP3 do Gemini AI → získá textový přepis
6. **API Call**: Odešle přepis + metadata na webové API včetně `audioUrl`
7. **Cleanup**: Smaže dočasné soubory

## 📊 API Payload

Systém odesílá na webové API následující JSON:

```json
{
    "Content": "Přepsaný text hlášení",
    "broadcastDateTime": "2025-06-05T20:27:43.511Z", 
    "audioUrl": "https://rozhlas.milesovice.cz/rozhlas/Hlášení 9.6..ogg"
}
```

## 🛠️ Troubleshooting

### SSL Certificate Issues (localhost)
Pro lokální vývoj s self-signed certifikáty je SSL verifikace vypnuta.

### Python 3.13 Compatibility
Projekt používá `audioop-lts` pro kompatibilitu s Python 3.13.

### CRON Job Logs
Na produkci jsou logy uloženy v `cron.log`:
```bash
tail -f cron.log
```

## 📝 Licence

Tento projekt je určen pro automatizaci zpracování veřejných hlášení obce Milešovice.

## ⚠️ Bezpečnostní upozornění

- **NIKDY** necommitujte `.env` soubor
- **NIKDY** necommitujte API klíče v kódu
- Pravidelně rotujte API klíče
- Používejte různé klíče pro vývoj a produkci 