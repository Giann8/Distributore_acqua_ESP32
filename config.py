# --- Modalita sviluppo ---
# True: boot.py e main.py non fanno nulla automaticamente (niente WiFi,
# niente avvio dispenser), la scheda resta subito libera alla REPL.
# False: funzionamento normale.
DEV_MODE = False

# ============================================
# CONFIGURAZIONE HARDWARE E RETE
# ============================================

# --- Pin OLED (I2C) ---
SDA_PIN = 21
SCL_PIN = 23
OLED_WIDTH = 128
OLED_HEIGHT = 64

# --- Pin relè / pompa ---
RELAY_PIN = 26
RELAY_ACTIVE_LOW = True  # True se il modulo relè è active-LOW (verificato nei test)

# --- Pin HX711 / cella di carico ---
HX711_DT_PIN = 4
HX711_SCK_PIN = 5

# Valori di calibrazione: aggiornali dopo aver eseguito calibrazione_hx711.py
HX711_OFFSET = -98932.6
HX711_SCALE_FACTOR = 91.2748  # raw per grammo

# --- LED di stato integrato ---
STATUS_LED_PIN = 2

# --- WiFi ---
WIFI_ENABLED = False   # False: salta del tutto WiFi/WebREPL, nessun tentativo
# Credenziali reali in wifi_secrets.py (non versionato, vedi README) per non
# tenerle in chiaro nel repository pubblico.
try:
    from wifi_secrets import WIFI_SSID, WIFI_PASSWORD
except ImportError:
    WIFI_SSID = ""
    WIFI_PASSWORD = ""
WIFI_CONNECT_TIMEOUT_S = 15
WIFI_MAX_RETRIES = 2  # tentativi aggiuntivi se il primo fallisce

# --- Pulsante conferma ---
BUTTON_PIN = 27
BUTTON_ACTIVE_LOW = True  # True se il pulsante collega a GND quando premuto (con pull-up interno)

# --- Logica di erogazione ---
BOTTLE_DETECT_THRESHOLD_G = 12   # sotto il peso di un bicchiere vuoto (~20g)
FILL_TARGET_G = 500              # quantita' da erogare, in grammi (= ml per acqua)
PUMP_STOP_MARGIN_CUP_G = 5       # anticipo di stop, bicchiere (volumi piccoli)
PUMP_STOP_MARGIN_BOTTLE_G = 15   # anticipo di stop, borraccia (volumi grandi)
CONFIRM_TIMEOUT_S = 10           # secondi di attesa per la conferma dell'utente
MAX_FILL_TIME_S = 120            # sicurezza: stop pompa forzato oltre questo tempo
CUP_QUANTITY_OPTIONS_ML = (25, 75, 100, 125)
BOTTLE_QUANTITY_OPTIONS_ML = (250, 500, 750, 1000)
QUANTITY_SELECTION_TIMEOUT_S = 4   # secondi di inattivita' prima di confermare la scelta
DISPENSE_START_DELAY_S = 3          # secondi di countdown prima di iniziare l'erogazione

# --- Auto-tara (correzione drift) ---
AUTO_TARE_DRIFT_G = 5           # fascia attorno allo zero considerata "normale"
AUTO_TARE_AFTER_S = 10          # secondi fuori fascia prima di ritarare in automatico

# --- Sicurezza sensore ---
SENSOR_ERROR_TIMEOUT_S = 15     # secondi di letture HX711 invalide (None) prima di arrendersi in attesa rimozione contenitore

# --- Filtro letture false (oltre al filtro su mediana in loadcell.read_average) ---
MAX_DEVIATION_FROM_LAST_G = 150  # scarta una lettura troppo distante dall'ultima valida

# --- Classificazione contenitore ---
# Basata sul peso A VUOTO misurato quando viene posato (media stabilizzata,
# non il primo valore grezzo). Misura i TUOI contenitori reali e aggiusta.
CONTAINER_WEIGHT_THRESHOLD_G = 100  # sotto = "Bicchiere", sopra (o uguale) = "Borraccia"
CONTAINER_CLASSIFY_CONSECUTIVE = 4  # letture consecutive coerenti per confermare il tipo