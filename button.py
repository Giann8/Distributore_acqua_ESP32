from machine import Pin
import time
import config


class Button:
    """Pulsante con pull-up interno e debounce software."""

    def __init__(self, debounce_ms=50):
        pull = Pin.PULL_UP if config.BUTTON_ACTIVE_LOW else Pin.PULL_DOWN
        self.pin = Pin(config.BUTTON_PIN, Pin.IN, pull)
        self.active_low = config.BUTTON_ACTIVE_LOW
        self.debounce_ms = debounce_ms
        self._last_state = self._raw_pressed()

    def _raw_pressed(self):
        val = self.pin.value()
        return (val == 0) if self.active_low else (val == 1)

    def is_pressed(self):
        """Lettura istantanea con debounce semplice (doppio campionamento)."""
        pressed = self._raw_pressed()
        if not pressed:
            self._last_state = False
            return False

        time.sleep_ms(self.debounce_ms)
        pressed = self._raw_pressed()
        if pressed:
            self._last_state = True
            return True

        self._last_state = False
        return False

    def wait_for_press(self, timeout_s):
        """Aspetta una pressione fino a timeout_s secondi.
        Ritorna True se premuto, False se scaduto il timeout."""
        start = time.ticks_ms()
        timeout_ms = int(timeout_s * 1000)
        while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
            if self.is_pressed():
                return True
            time.sleep_ms(20)
        return False
