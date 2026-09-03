from machine import Pin
import time
import config


class LoadCell:
    """Driver per HX711 + conversione in grammi usando offset e
    scale_factor calcolati con calibrazione_hx711.py (vedi config.py)."""

    def __init__(self):
        # Usa pull-up sul DT per evitare letture fluttuanti quando HX711 è in idle.
        self.dt = Pin(config.HX711_DT_PIN, Pin.IN, Pin.PULL_UP)
        self.sck = Pin(config.HX711_SCK_PIN, Pin.OUT)
        self.sck.value(0)
        self.offset = config.HX711_OFFSET
        self.scale_factor = config.HX711_SCALE_FACTOR
        self._last_valid_raw = None

    def read_raw(self, timeout_cycles=200000):
        """Legge un singolo valore grezzo a 24 bit (signed). Ritorna None
        se l'HX711 non risponde entro il timeout (es. cavi scollegati)."""
        timeout = 0
        while self.dt.value() == 1:
            time.sleep_us(10)
            timeout += 1
            if timeout > timeout_cycles:
                return None

        count = 0
        for _ in range(24):
            self.sck.value(1)
            count = count << 1
            self.sck.value(0)
            if self.dt.value():
                count += 1

        # 25esimo impulso: guadagno 128, canale A (default)
        self.sck.value(1)
        self.sck.value(0)

        if count & 0x800000:
            count -= 0x1000000

        return count

    def read_average(self, n=10, delay=0.03, max_deviation_g=200, allow_jump=False):
        """Media di n letture con reiezione degli outlier: scarta valori
        troppo lontani dalla mediana del gruppo (es. spike da rumore
        elettrico durante l'erogazione), poi fa la media dei restanti.
        Se allow_jump=False, scarta inoltre l'intera media quando è troppo
        distante dall'ultima lettura valida e i campioni non concordano tra
        loro (rumore isolato, non un vero cambio di peso). Usa allow_jump=True
        nei punti dove un salto di peso reale è atteso (tara, classificazione
        contenitore), altrimenti un salto legittimo rischia di restare
        "congelato" sul vecchio valore. Ritorna None se nessuna lettura riesce."""
        readings = []
        for _ in range(n):
            val = self.read_raw()
            if val is not None:
                readings.append(val)
            time.sleep(delay)

        if not readings:
            return None

        if len(readings) < 3:
            avg = sum(readings) / len(readings)
        else:
            sorted_r = sorted(readings)
            mid = len(sorted_r) // 2
            median = sorted_r[mid] if len(sorted_r) % 2 else (sorted_r[mid - 1] + sorted_r[mid]) / 2

            # soglia di scarto in unita' raw (converte grammi -> raw usando scale_factor)
            max_deviation_raw = max_deviation_g * abs(self.scale_factor)

            filtered = [r for r in readings if abs(r - median) <= max_deviation_raw]
            if not filtered:
                filtered = [median]  # tutti scartati (improbabile): tieni almeno la mediana

            avg = sum(filtered) / len(filtered)

        if not allow_jump and self._last_valid_raw is not None:
            max_deviation_from_last_raw = config.MAX_DEVIATION_FROM_LAST_G * abs(self.scale_factor)
            if abs(avg - self._last_valid_raw) > max_deviation_from_last_raw:
                # se i campioni grezzi concordano tra loro è un vero cambio di peso, non rumore
                agreeing = [r for r in readings if abs(r - avg) <= max_deviation_from_last_raw]
                if len(agreeing) < len(readings) / 2:
                    return self._last_valid_raw

        self._last_valid_raw = avg
        return avg

    def is_connected(self):
        return self.read_raw() is not None

    def get_weight_grams(self, n=10, allow_jump=False):
        """Ritorna il peso in grammi usando offset/scale_factor da config.
        Ritorna None se la lettura fallisce."""
        raw = self.read_average(n, allow_jump=allow_jump)
        if raw is None:
            return None
        return (raw - self.offset) / self.scale_factor

    def tare(self, n=20):
        """Ricalcola l'offset a runtime (piattaforma deve essere vuota).
        Utile per tarare il peso del contenitore prima di ogni erogazione.
        Usa sempre allow_jump=True: la tara deve accettare il nuovo peso
        anche se molto diverso dall'ultima lettura valida."""
        val = self.read_average(n, allow_jump=True)
        if val is not None:
            self.offset = val
        return self.offset