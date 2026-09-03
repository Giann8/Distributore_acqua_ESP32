from machine import Pin
import time

import config
import wifi
from display import Display
from relay import Relay
from loadcell import LoadCell
from button import Button
from dispense import Dispenser

def run_startup_sequence(display, relay, loadcell, status_led):
    # 1. Schermata di benvenuto
    display.show(["Dispenser Acqua", "", "Avvio in corso..."], delay=2)

    # 2. Test relè (verifica solo che il pin risponda al comando)
    display.show(["Test hardware", "", "Rele..."])
    relay_ok = relay.self_test()
    time.sleep(0.5)

    # 3. Test cella di carico (verifica che HX711 risponda)
    display.show(["Test hardware", "", "Cella di carico..."])
    hx711_ok = loadcell.is_connected()
    time.sleep(0.5)

    display.show([
        "Test hardware",
        "Rele:  " + ("OK" if relay_ok else "ERRORE"),
        "Cella: " + ("OK" if hx711_ok else "ERRORE"),
    ], delay=2)

    # 4. Stato WiFi (boot.py ha già tentato la connessione, se abilitato)
    if not config.WIFI_ENABLED:
        display.show(["WiFi disattivato", "", "Modalita offline"], delay=2)
        status_led.value(0)
        wifi_ok = False
    else:
        display.show(["Verifica WiFi", "", config.WIFI_SSID])

        if wifi.is_connected():
            ip = wifi.get_ip()
            display.show(["WiFi connesso", "", ip], delay=2)
            status_led.value(1)
            wifi_ok = True
        else:
            # boot.py ha già provato con retry; se siamo ancora qui offline,
            # un ultimo tentativo diretto da main.py
            wifi_ok, ip = wifi.connect(retries=1)
            if wifi_ok:
                display.show(["WiFi connesso", "", ip], delay=2)
                status_led.value(1)
            else:
                display.show(["WiFi NON connesso", "", "Modalita offline"], delay=2)
                status_led.value(0)

    # 5. Schermata pronta
    display.show([
        "Dispenser pronto",
        "WiFi:  " + ("ON" if wifi_ok else "OFF"),
        "Cella: " + ("OK" if hx711_ok else "ERR"),
    ])

    print("Avvio completato.")
    print("WiFi:", wifi.get_ip() if wifi_ok else "non connesso")
    print("HX711 connesso:", hx711_ok)

    return relay_ok, hx711_ok, wifi_ok


def main():
    display = Display()
    relay = Relay()
    loadcell = LoadCell()
    button = Button()
    status_led = Pin(config.STATUS_LED_PIN, Pin.OUT)

    relay_ok, hx711_ok, wifi_ok = run_startup_sequence(display, relay, loadcell, status_led)

    if not relay_ok:
        display.show(["ERRORE", "Rele", "non disponibile"])
        return

    if not hx711_ok:
        display.show(["ERRORE", "Cella di carico", "non disponibile"])
        return

    # Avvia subito il ciclo del dispenser; il Dispenser aspetta che la
    # borraccia venga posizionata prima di chiedere conferma con il pulsante.
    print("Avvio ciclo dispenser: posiziona la borraccia e premi quando richiesto.")
    display.show([
        "Dispenser pronto",
        "Posiziona la borraccia",
        "Poi premi il pulsante",
    ])
    dispenser = Dispenser(loadcell, relay, display, button)
    dispenser.run_forever()


if __name__ == "__main__":
    if config.DEV_MODE:
        print("=== MODALITA' SVILUPPO ATTIVA (config.DEV_MODE = True) ===")
        print("main.py non si avvia automaticamente.")
    else:
        main()