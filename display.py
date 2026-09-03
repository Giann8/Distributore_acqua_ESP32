from machine import Pin, I2C
import ssd1306
import time
import config


class Display:
    """Wrapper attorno al display OLED SSD1306. Se il display non è
    collegato/rilevato, tutti i metodi diventano no-op silenziosi,
    così il resto del programma continua a funzionare senza crash."""

    def __init__(self):
        self.oled = None
        try:
            i2c = I2C(0, scl=Pin(config.SCL_PIN), sda=Pin(config.SDA_PIN), freq=400000)
            if i2c.scan():
                self.oled = ssd1306.SSD1306_I2C(config.OLED_WIDTH, config.OLED_HEIGHT, i2c)
            else:
                print("Display: nessun dispositivo I2C trovato")
        except Exception as e:
            print("Display: inizializzazione fallita:", e)

    @property
    def available(self):
        return self.oled is not None

    def _fit(self, text, max_chars=16):
        text = "" if text is None else str(text)
        if len(text) <= max_chars:
            return text
        if max_chars <= 3:
            return text[:max_chars]
        return text[: max_chars - 3] + "..."

    def _center_x(self, text):
        return max(0, int((self.oled.width - (len(text) * 8)) / 2))

    def _draw_body(self, lines, start_y=18, line_gap=14):
        for i, line in enumerate(lines):
            if line:
                text = self._fit(line)
                self.oled.text(text, self._center_x(text), start_y + (i * line_gap))

    def _draw_frame(self, title, lines=None, footer=None):
        self.oled.fill(0)
        title_text = self._fit(title)
        self.oled.text(title_text, self._center_x(title_text), 2)
        self.oled.hline(6, 12, self.oled.width - 12, 1)
        if lines:
            self._draw_body(lines)
        if footer:
            footer_text = self._fit(footer)
            self.oled.text(footer_text, self._center_x(footer_text), self.oled.height - 10)

    def show(self, lines, delay=0):
        """Mostra una lista di righe di testo. delay=0 non aspetta."""
        if not self.available:
            return
        if not lines:
            self.oled.fill(0)
            self.oled.show()
            return
        title = lines[0]
        body = lines[1:] if len(lines) > 1 else []
        footer = None
        if len(lines) > 3:
            footer = lines[3]
        self._draw_frame(title, body, footer=footer)
        self.oled.show()
        if delay:
            time.sleep(delay)

    def clear(self):
        if self.available:
            self.oled.fill(0)
            self.oled.show()

    def show_progress(self, percent, lines=None):
        """Mostra righe di testo opzionali sopra una barra di avanzamento
        percentuale (0-100) disegnata a pixel in basso sullo schermo."""
        if not self.available:
            return
        percent = max(0, min(100, percent))
        title = lines[0] if lines else "Erogazione"
        body = lines[1:] if lines and len(lines) > 1 else []
        self._draw_frame(title, body, footer="{}%".format(percent))

        bar_x, bar_h = 8, 10
        bar_y = self.oled.height - bar_h - 16
        bar_w = self.oled.width - (bar_x * 2)
        self.oled.rect(bar_x, bar_y, bar_w, bar_h, 1)
        fill_w = int((bar_w - 2) * percent / 100)
        if fill_w > 0:
            self.oled.fill_rect(bar_x + 1, bar_y + 1, fill_w, bar_h - 2, 1)
        self.oled.show()

    def show_loading(self, lines, tick=0):
        """Schermata di attesa con testo centrato e un indicatore animato
        (puntini che avanzano in base a tick, es. il secondo di un countdown)."""
        if not self.available:
            return
        title = lines[0] if lines else "Attendere"
        body = lines[1:] if lines and len(lines) > 1 else []
        dots = "." * ((tick % 3) + 1)
        self._draw_frame(title, body, footer=dots)
        self.oled.show()
