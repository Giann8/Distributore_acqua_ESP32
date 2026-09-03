# Distributore_acqua_ESP32

Distributore d'acqua semi-autonomo basato su ESP32 e MicroPython. Il sistema usa una cella di carico con HX711 per rilevare il peso del contenitore, un relè per controllare la pompa, un pulsante fisico per la conferma utente e un display OLED SSD1306 per mostrare lo stato del ciclo.

Il progetto è pensato per gestire il riempimento in modo guidato ma semplice: l'utente posiziona il contenitore, conferma con il pulsante e seleziona il volume da erogare. Il firmware distingue tra bicchiere e borraccia, applica filtri sulle letture del sensore e aggiorna il display con una UI più leggibile.

## Funzionalità

- Rilevamento del contenitore tramite cella di carico HX711
- Classificazione tra bicchiere e borraccia
- Selezione del volume tramite pulsante fisico
- Controllo della pompa con relè
- Interfaccia OLED con schermate di stato, barra di progresso e loading screen
- Tara automatica e gestione del drift del sensore
- Modalità WiFi opzionale, senza bloccare il funzionamento del dispenser
- Modalità sviluppo per avvio manuale da REPL

## Tecnologie

- ESP32
- MicroPython
- HX711 + cella di carico
- OLED SSD1306
- Relè per pompa
- Pulsante fisico
- WiFi opzionale

## Struttura principale

- `main.py` avvia il ciclo del distributore
- `dispense.py` contiene la logica di erogazione
- `loadcell.py` gestisce lettura e conversione del peso
- `display.py` gestisce il display OLED
- `relay.py` controlla il relè della pompa
- `button.py` gestisce il pulsante
- `config.py` raccoglie tutti i parametri hardware e di logica
- `boot.py` gestisce l'avvio iniziale e il WiFi

## Requisiti

- ESP32 compatibile con MicroPython
- HX711 collegato alla cella di carico
- OLED SSD1306 I2C
- Relè per la pompa
- Pulsante fisico
- Alimentazione adeguata per pompa e logica

## Avvio

1. Caricare i file Python sull'ESP32.
2. Collegare l'hardware secondo la configurazione in `config.py`.
3. Riavviare la scheda.
4. Il sistema entra nel ciclo di erogazione e attende il contenitore.

Per accedere alla REPL o riavviare la scheda tramite `mpremote`, usa il comando:

```bash
mpremote connect /dev/tty.XXXX repl
```

Poi esci con `Ctrl+D` oppure esegui un reset da terminale con:

```bash
mpremote connect /dev/tty.XXXX reset
```

## Configurazione

I parametri hardware e di logica si trovano in `config.py`.

Le credenziali WiFi NON sono in `config.py` (per non versionarle in chiaro):
copia `wifi_secrets.example.py` in `wifi_secrets.py` (file ignorato da Git) e
inserisci lì `WIFI_SSID`/`WIFI_PASSWORD`. Se `wifi_secrets.py` non esiste,
`config.py` usa credenziali vuote e il sistema funziona comunque in modalità
offline (`WIFI_ENABLED = False`).

**Attenzione (nota di sicurezza)**: prima di questo fix, la password WiFi era
versionata in chiaro nella cronologia Git. Rimuoverla dal file attuale non la
revoca: se il repository è pubblico o è stato clonato/forkato, la password
del router/hotspot va comunque cambiata.

Le impostazioni più importanti sono:

- pin OLED I2C
- pin HX711
- pin relè
- pin pulsante
- soglia di classificazione contenitore
- quantità selezionabili
- margini di stop erogazione

## Licenza

Questo progetto è rilasciato con licenza GNU GPL v3.0.
