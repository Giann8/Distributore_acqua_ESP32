# Documentazione tecnica

## 0. Metadati

- **Progetto:** Distributore_acqua_ESP32
- **Autore:** Graziano Nobile
- **Repository:** https://github.com/Giann8/Distributore_acqua_ESP32.git
- **Licenza:** GNU GPL v3.0
- **Data presentazione:** settembre/ottobre 2026

## 1. Descrizione del progetto

Il progetto realizza un distributore d'acqua semi-autonomo basato su ESP32 e MicroPython. Il sistema misura il peso del contenitore con una cella di carico gestita da HX711, mostra le informazioni su un display OLED SSD1306 e controlla la pompa tramite relè.

L'utente interagisce con un pulsante fisico per confermare la presenza del contenitore e per scegliere il volume da erogare. Il software distingue tra bicchiere e borraccia, applica filtri anti-rumore alle letture del sensore e aggiorna il display con una grafica più moderna, comprensiva di barra di avanzamento e schermate di attesa.

## 2. Obiettivi

- Automatizzare il riempimento di acqua in modo semplice e guidato
- Ridurre gli errori di lettura della cella di carico
- Separare i comportamenti tra bicchiere e borraccia
- Offrire un'interfaccia OLED chiara e leggibile
- Mantenere il sistema funzionante anche con WiFi disattivato

## 3. Architettura software

### File principali

- `boot.py` - avvio iniziale e gestione WiFi opzionale
- `main.py` - punto di ingresso dell'applicazione
- `dispense.py` - logica del ciclo di erogazione
- `loadcell.py` - lettura del peso e conversione in grammi
- `display.py` - gestione del display OLED
- `relay.py` - controllo della pompa tramite relè
- `button.py` - gestione del pulsante fisico
- `wifi.py` - connessione WiFi opzionale
- `config.py` - parametri hardware e logici

### Flusso di esecuzione

1. All'avvio, `boot.py` prepara il sistema e tenta il WiFi solo se abilitato.
2. `main.py` inizializza display, relè, cella di carico, pulsante e LED di stato.
3. Il ciclo del distributore aspetta che il contenitore venga posizionato.
4. Il peso viene stabilizzato e il contenitore viene classificato.
5. L'utente conferma con il pulsante e sceglie il volume.
6. La pompa parte e si ferma quando viene raggiunta la soglia di stop.
7. Il display mostra il progresso dell'erogazione e lo stato finale.

## 4. Interfaccia OLED

Il display usa una struttura visiva più ordinata rispetto al semplice testo libero.

### Schermate principali

- **Stato iniziale**: messaggio di sistema pronto
- **Attesa contenitore**: testo centrato e indicatore di attesa
- **Conferma utente**: richiesta di pressione del pulsante
- **Selezione volume**: menu con volume corrente
- **Erogazione**: barra di progresso percentuale
- **Completamento**: messaggio finale e invito a rimuovere il contenitore

### Scelte di design

- Titoli centrati per migliorare la leggibilità
- Separatore superiore per dare una gerarchia visiva chiara
- Corpo testo distribuito con spazi più regolari
- Barra di avanzamento in basso per mostrare il riempimento in tempo reale
- Schermata di loading durante il countdown prima dell'erogazione

## 5. Logica di classificazione contenitore

Il sistema distingue tra due categorie:

- **Bicchiere**: peso inferiore a 100 g
- **Borraccia**: peso pari o superiore a 100 g

La classificazione usa letture consecutive coerenti per evitare oscillazioni vicino alla soglia.

## 6. Quantità selezionabili

Le quantità dipendono dal tipo di contenitore rilevato.

### Bicchiere

- 25 ml
- 75 ml
- 100 ml
- 125 ml

### Borraccia

- 250 ml
- 500 ml
- 750 ml
- 1000 ml

## 7. Gestione del sensore

`loadcell.py` applica due livelli di filtro:

- media con reiezione degli outlier interni al gruppo di campioni
- scarto di letture troppo distanti dall'ultima lettura valida

Questo aiuta a ridurre le letture false senza bloccare il sistema in presenza di un vero cambio di peso.

## 8. Sicurezza e robustezza

- La pompa viene spenta in ogni caso nei blocchi di sicurezza del codice
- Esiste un timeout massimo di erogazione
- Il sistema continua a funzionare anche se il WiFi non si connette
- Il display è progettato per degradare in modo silenzioso se non viene rilevato

## 9. Configurazione hardware

I pin e i parametri principali sono raccolti in `config.py`.

Tra i valori principali:

- pin I2C per OLED
- pin HX711
- pin relè
- pin pulsante
- soglia di classificazione contenitore
- soglie di filtro letture
- margini di stop per bicchiere e borraccia

## 10. Note di utilizzo

### Caricamento file su ESP32

I file possono essere caricati con `mpremote`.

Esempio:

```bash
mpremote connect /dev/tty.XXXX fs cp main.py :main.py
```

### Avvio della REPL

```bash
mpremote connect /dev/tty.XXXX repl
```

### Reset della scheda

```bash
mpremote connect /dev/tty.XXXX reset
```

## 11. Licenza

Il progetto è distribuito con licenza GNU GPL v3.0.

## 12. Autore

Graziano Nobile
