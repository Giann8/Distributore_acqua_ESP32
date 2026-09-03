import time
import config


class Dispenser:
    """Logica di erogazione: monitora la cella di carico in continuo,
    quando rileva un peso sopra soglia chiede conferma all'utente
    (pulsante), poi eroga finche' non raggiunge il target."""

    def __init__(self, loadcell, relay, display, button):
        self.loadcell = loadcell
        self.relay = relay
        self.display = display
        self.button = button

    def _idle_weight(self, n=5, allow_jump=False):
        """Peso attuale rispetto all'ultima tara nota (baseline = 0 a vuoto)."""
        w = self.loadcell.get_weight_grams(n=n, allow_jump=allow_jump)
        return w

    def wait_for_bottle(self):
        """Aspetta che la borraccia venga posata sulla cella."""
        self.display.show([
            "Dispenser pronto",
            "Posiziona la borraccia",
            "Peso in lettura",
        ])

        # Calcola baseline iniziale (media di letture a vuoto) per rilevare
        # il salto di peso. Se la lettura non è valida, mostra N/D.
        baseline_samples = []
        sample_count = 5
        for _ in range(sample_count):
            # allow_jump: qui un salto e' atteso solo se una borraccia era gia'
            # rimasta sulla piattaforma da un ciclo precedente, non vogliamo che
            # resti congelata sul vecchio valore.
            v = self._idle_weight(n=3, allow_jump=True)
            if v is not None:
                baseline_samples.append(v)
            time.sleep(0.1)

        baseline = (sum(baseline_samples) / len(baseline_samples)) if baseline_samples else 0
        print('Baseline weight:', baseline)

        tolerance = 50  # grammi di tolleranza per evitare oscillazioni
        required_consecutive = 3
        consecutive = 0

        # Auto-tara: se il peso resta fuori dalla fascia "vicino a zero" per
        # troppo tempo (drift del sensore, non una borraccia vera - resta
        # comunque sotto la soglia di rilevamento), ritara automaticamente.
        drift_start = None

        while True:
            # allow_jump=True: qui si attende esattamente il salto di peso che
            # segnala la borraccia posata, non va scartato come rumore.
            w = self._idle_weight(n=3, allow_jump=True)
            if w is None:
                consecutive = 0
                drift_start = None
                self.display.show([
                    "Dispenser pronto",
                    "Errore lettura",
                    "HX711 N/D",
                ])
                print('HX711 read: None')
            else:
                # mostra peso live su display e seriale
                self.display.show([
                    "Dispenser pronto",
                    "Peso: {:.0f} g".format(w),
                    "Appoggia bene il contenitore",
                ])
                print('Peso: {:.2f} g'.format(w))

                # rileva salto rispetto alla baseline con tolleranza
                if (w - baseline) >= tolerance and w >= config.BOTTLE_DETECT_THRESHOLD_G:
                    consecutive += 1
                    drift_start = None
                    if consecutive >= required_consecutive:
                        return w
                else:
                    consecutive = 0

                    # Drift: peso stabilmente fuori dalla fascia [-DRIFT, +DRIFT]
                    # ma comunque sotto la soglia borraccia -> non è un oggetto
                    # posato, è solo lo zero che si è spostato.
                    if abs(w - baseline) > config.AUTO_TARE_DRIFT_G:
                        if drift_start is None:
                            drift_start = time.ticks_ms()
                        elif time.ticks_diff(time.ticks_ms(), drift_start) >= config.AUTO_TARE_AFTER_S * 1000:
                            print('Auto-tara: drift rilevato per', config.AUTO_TARE_AFTER_S, 's, ritaro.')
                            self.display.show(["Auto-taratura", "", "Correzione drift"])
                            self.loadcell.tare(n=15)
                            baseline = 0
                            drift_start = None
                            time.sleep(0.3)
                    else:
                        drift_start = None

            time.sleep(0.25)

    def ask_confirmation(self):
        """Richiede la conferma tramite pulsante."""
        timeout_ms = int(config.CONFIRM_TIMEOUT_S * 1000)
        start = time.ticks_ms()
        self.display.show([
            "Conferma presenza",
            "Premi il pulsante",
            "per continuare",
        ])
        while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
            w = self._idle_weight(n=3)
            if w is None:
                self.display.show([
                    "Conferma presenza",
                    "Lettura instabile",
                    "Premi quando OK",
                ])
            else:
                self.display.show([
                    "Conferma presenza",
                    "Peso: {:.0f} g".format(w),
                    "Premi per confermare",
                ])

            if self.button.is_pressed():
                # quando l'utente preme, controlla che la lettura sia valida
                if w is not None and w >= config.BOTTLE_DETECT_THRESHOLD_G:
                    return True
                else:
                    # mostra messaggio e continua ad aspettare
                    self.display.show(["Lettura instabile", "Riposiziona", "e riprova"], delay=1)

            time.sleep(0.1)
        return False

    def select_quantity_ml(self, container):
        """Cicla tra i volumi del tipo di contenitore rilevato usando i click
        del pulsante. La scelta viene confermata automaticamente dopo un
        timeout di inattivita'."""
        options = config.CUP_QUANTITY_OPTIONS_ML if container == "Bicchiere" else config.BOTTLE_QUANTITY_OPTIONS_ML
        idx = 0
        last_press_ms = time.ticks_ms()

        # Evita che un bottone ancora premuto nella fase precedente cambi
        # subito la selezione.
        while self.button.is_pressed():
            time.sleep_ms(20)

        self.display.show([
            "Scegli volume",
            "{} ml".format(options[idx]),
            "Premi per cambiare",
        ])
        print("Volume selezionato:", options[idx], "ml")

        while True:
            # rileva un singolo click (raw check + debounce) per evitare
            # che wait_for_press blocchi o venga confuso da timeout brevi
            if self.button._raw_pressed():
                # debounce
                time.sleep_ms(self.button.debounce_ms)
                if self.button._raw_pressed():
                    # attendi rilascio
                    while self.button._raw_pressed():
                        time.sleep_ms(20)
                    idx = (idx + 1) % len(options)
                    last_press_ms = time.ticks_ms()
                    self.display.show([
                        "Scegli volume",
                        "{} ml".format(options[idx]),
                        "Premi per cambiare",
                    ])
                    print("Volume selezionato:", options[idx], "ml")

            if time.ticks_diff(time.ticks_ms(), last_press_ms) > config.QUANTITY_SELECTION_TIMEOUT_S * 1000:
                return options[idx]

            time.sleep_ms(50)

    def countdown_then_dispense(self, target_ml, container):
        """Manda in esecuzione il countdown prima di avviare la pompa."""
        for seconds in range(config.DISPENSE_START_DELAY_S, 0, -1):
            self.display.show_loading([
                "Erogazione in",
                "{} secondi".format(seconds),
                "{} ml".format(target_ml),
            ], tick=seconds)
            time.sleep(1)

        self.dispense(target_ml, container)

    def dispense(self, target_ml=None, container=None):
        """Esegue l'erogazione vera e propria."""
        if target_ml is None:
            target_ml = config.FILL_TARGET_G

        self.display.show(["Taratura...", "", "Non muovere"])
        self.loadcell.tare(n=15)
        time.sleep(0.3)

        target_grams = target_ml
        pump_stop_margin_g = config.PUMP_STOP_MARGIN_CUP_G if container == "Bicchiere" else config.PUMP_STOP_MARGIN_BOTTLE_G
        start_time = time.ticks_ms()
        stop_confirm_count = 0
        STOP_CONFIRM_NEEDED = 3  # letture consecutive sopra soglia prima di fermare

        self.display.show(["Erogazione...", "0 / {} ml".format(target_ml)])

        try:
            self.relay.on()

            while True:
                elapsed_s = time.ticks_diff(time.ticks_ms(), start_time) / 1000

                if elapsed_s > config.MAX_FILL_TIME_S:
                    self.display.show(["ERRORE", "Timeout erogazione", "Pompa fermata"], delay=3)
                    return False

                current = self.loadcell.get_weight_grams(n=3)
                if current is None:
                    self.display.show([
                        "Erogazione",
                        "Lettura instabile",
                        "Controlla cablaggio",
                    ])
                    time.sleep(0.1)
                    continue

                self.display.show_progress(
                    int(min(100, max(0, current / target_grams * 100))),
                    lines=["Erogazione...", "{:.0f} / {} ml".format(current, target_ml)],
                )

                if current >= target_grams - pump_stop_margin_g:
                    stop_confirm_count += 1
                    if stop_confirm_count >= STOP_CONFIRM_NEEDED:
                        break
                else:
                    stop_confirm_count = 0
        finally:
            # SICUREZZA: la pompa si spegne SEMPRE qui, qualsiasi cosa
            # succeda sopra (eccezione, errore sensore, blocco, ecc.)
            self.relay.off()

        time.sleep(1)
        final_weight = self.loadcell.get_weight_grams(n=10)

        self.display.show([
            "Completato",
            "{:.0f} ml erogati".format(final_weight if final_weight is not None else target_ml),
            "Rimuovi il contenitore",
        ], delay=3)
        return True

    def _classify_container(self):
        """Classifica bicchiere/borraccia richiedendo N letture consecutive
        coerenti (isteresi), per non oscillare vicino alla soglia."""
        threshold = config.CONTAINER_WEIGHT_THRESHOLD_G
        needed = config.CONTAINER_CLASSIFY_CONSECUTIVE
        consecutive = 0
        container = None
        w_stable = None
        # limite di tentativi per evitare un blocco indefinito se le letture
        # oscillano continuamente sul confine della soglia
        for _ in range(needed * 5):
            w_stable = self.loadcell.get_weight_grams(n=15, allow_jump=True)
            candidate = "Borraccia" if (w_stable is not None and w_stable >= threshold) else "Bicchiere"
            if candidate == container:
                consecutive += 1
            else:
                container = candidate
                consecutive = 1
            if consecutive >= needed:
                break
            time.sleep(0.1)
        return container, w_stable

    def _wait_for_container_removed(self):
        """Aspetta che il peso scenda sotto soglia rimozione; si arrende dopo
        SENSOR_ERROR_TIMEOUT_S di letture invalide per non restare bloccati
        all'infinito se la cella di carico smette di rispondere a meta' sessione."""
        sensor_error_start = None
        while True:
            w = self._idle_weight(n=3, allow_jump=True)
            self.display.show([
                "Rimuovi il contenitore",
                "",
                "Peso: {:.0f} g".format(w if w is not None else 0),
            ])
            if w is not None and w < config.BOTTLE_DETECT_THRESHOLD_G:
                return
            if w is None:
                if sensor_error_start is None:
                    sensor_error_start = time.ticks_ms()
                elif time.ticks_diff(time.ticks_ms(), sensor_error_start) >= config.SENSOR_ERROR_TIMEOUT_S * 1000:
                    print('Cella di carico non risponde, riprendo il ciclo per sicurezza.')
                    return
            else:
                sensor_error_start = None
            time.sleep(0.3)

    def run_once(self):
        """Ciclo completo: aspetta borraccia -> chiede conferma -> seleziona volume -> eroga."""
        w = self.wait_for_bottle()

        container, w_stable = self._classify_container()
        if w_stable is None:
            w_stable = w

        # Mostra il tipo e il peso prima di chiedere conferma
        self.display.show([
            "{} rilevata".format(container),
            "Peso: {:.0f} g".format(w if w is not None else 0),
            "Premi per confermare",
        ])

        if not self.ask_confirmation():
            self.display.show(["Annullato", "", "Rimuovi il contenitore"], delay=2)
            self._wait_for_container_removed()
            return

        quantity_ml = self.select_quantity_ml(container)
        self.countdown_then_dispense(quantity_ml, container)

        self._wait_for_container_removed()
        # Una volta rimossa la borraccia, rifacciamo una tara per aggiornare
        # la baseline del sistema (piattaforma vuota)
        self.display.show_loading(["Taratura...", "Rimuovi il contenitore", "Attendere"], tick=1)
        self.loadcell.tare(n=20)
        time.sleep(0.2)
        self.display.show(["Tara aggiornata", "Sistema pronto", ""], delay=1)

    def run_forever(self):
        while True:
            try:
                self.run_once()
            except Exception as e:
                # SICUREZZA: qualsiasi errore imprevisto nel ciclo spegne
                # comunque la pompa prima di segnalare e riprendere.
                self.relay.off()
                print("Errore nel ciclo dispenser, pompa spenta per sicurezza:", e)
                self.display.show(["ERRORE", "Pompa fermata", "Riavvio ciclo..."], delay=3)