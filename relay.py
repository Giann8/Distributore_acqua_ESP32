from machine import Pin
import time
import config


class Relay:
    """Controllo del relè/pompa. Gestisce internamente la logica
    active-low/active-high, così il resto del codice usa solo on()/off()."""

    def __init__(self):
        self.pin = Pin(config.RELAY_PIN, Pin.OUT)
        self.active_low = config.RELAY_ACTIVE_LOW
        self.off()  # sicurezza: pompa sempre spenta all'inizializzazione

    def on(self):
        self.pin.value(0 if self.active_low else 1)

    def off(self):
        self.pin.value(1 if self.active_low else 0)

    def is_on(self):
        state = self.pin.value()
        return (state == 0) if self.active_low else (state == 1)

    def pulse(self, seconds):
        """Accende per un tempo definito, poi spegne. Bloccante."""
        self.on()
        time.sleep(seconds)
        self.off()

    def self_test(self):
        """Test rapido: accende e spegne per verificare che il pin risponda.
        Non conferma elettricamente che il relè abbia scattato (serve un
        sensore aggiuntivo per quello), solo che il comando è stato inviato."""
        try:
            self.on()
            time.sleep(0.3)
            self.off()
            return True
        except Exception as e:
            print("Relay self_test fallito:", e)
            return False
