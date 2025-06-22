#!/bin/bash
set -e

# DEMO VERZE DEPLOY SCRIPTU
# Pro skutečné nasazení:
# 1. Zkopírujte tento soubor jako deploy.sh
# 2. Vyplňte skutečné API klíče v sekci "Produkční proměnné"
# 3. Spusťte ./deploy.sh

echo "--- Zahajuji konfiguraci produkčního prostředí pro BroadcastAnnouncements ---"

# --- Konfigurace ---
VENV_PATH=".venv"
LOG_FILE="cron.log"
CRON_COMMENT="# BroadcastAnnouncements Cron Job"

# Produkční proměnné - MUSÍ BÝT NASTAVENY PŘED SPUŠTĚNÍM!
# Nastavte tyto proměnné před spuštěním deploy.sh
if [ -z "$PROD_GEMINI_API_KEY" ] || [ -z "$PROD_WEB_API_KEY" ] || [ -z "$PROD_WEB_API_ENDPOINT" ]; then
    echo "CHYBA: Musíte nastavit environment variables před spuštěním:"
    echo "export PROD_GEMINI_API_KEY='your_gemini_api_key'"
    echo "export PROD_WEB_API_KEY='your_web_api_key'"
    echo "export PROD_WEB_API_ENDPOINT='your_web_api_endpoint'"
    exit 1
fi

# --- 1. Instalace systémových závislostí ---
echo "--> Instaluji systémové závislosti (python3-venv, ffmpeg)..."
sudo apt-get update
sudo apt-get install -y python3-venv ffmpeg

# --- 2. Vytvoření produkčního .env souboru ---
echo "--> Vytvářím produkční .env soubor s API klíči..."
cat << EOF > .env
GEMINI_API_KEY="$PROD_GEMINI_API_KEY"
WEB_API_KEY="$PROD_WEB_API_KEY"
WEB_API_ENDPOINT="$PROD_WEB_API_ENDPOINT"
EOF

# --- 3. Nastavení Python virtuálního prostředí ---
echo "--> Nastavuji virtuální prostředí a instaluji závislosti..."
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
fi
source "$VENV_PATH/bin/activate"
pip install -r requirements.txt
deactivate

# --- 4. Nastavení CRON úlohy ---
echo "--> Nastavuji CRON úlohu pro spouštění každých 5 minut..."
PYTHON_EXEC="$(pwd)/$VENV_PATH/bin/python"
SCRIPT_PATH="$(pwd)/main.py"
# Cron job se musí spouštět ze správného adresáře, aby našel .env a další soubory
CRON_JOB="*/5 * * * * cd $(pwd) && $PYTHON_EXEC $SCRIPT_PATH >> $LOG_FILE 2>&1"

# Idempotentní přidání cron jobu: odstraní starý (pokud existuje) a přidá nový
(crontab -l 2>/dev/null | grep -v -F "$CRON_COMMENT" || true) | { cat; echo "$CRON_JOB $CRON_COMMENT"; } | crontab -

echo "--> CRON úloha byla úspěšně nastavena."

# --- 5. Testovací spuštění ---
echo "--> Spouštím aplikaci jednou pro ověření funkčnosti..."
$PYTHON_EXEC $SCRIPT_PATH

echo ""
echo "--- Nasazení bylo úspěšně dokončeno! ---"
echo "Aplikace je v $(pwd) a bude se spouštět každých 5 minut."
echo "Logy ze spuštění přes CRON naleznete v souboru: $LOG_FILE" 