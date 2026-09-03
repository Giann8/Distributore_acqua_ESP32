import network
import time
import config


def connect(retries=None):
    """Prova a connettersi al WiFi, con eventuali tentativi aggiuntivi
    se il primo fallisce (comportamento osservato: a volte il primo
    tentativo fallisce e il secondo riesce).

    Ritorna una tupla (connected: bool, ip: str o None).
    """
    if retries is None:
        retries = config.WIFI_MAX_RETRIES

    wlan = network.WLAN(network.STA_IF)

    for attempt in range(retries + 1):
        wlan.active(False)
        time.sleep(1)
        wlan.active(True)
        time.sleep(1)

        if wlan.isconnected():
            return True, wlan.ifconfig()[0]

        print("WiFi tentativo {}/{}...".format(attempt + 1, retries + 1))
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

        timeout = config.WIFI_CONNECT_TIMEOUT_S
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

        if wlan.isconnected():
            return True, wlan.ifconfig()[0]

    return False, None


def is_connected():
    wlan = network.WLAN(network.STA_IF)
    return wlan.active() and wlan.isconnected()


def get_ip():
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        return wlan.ifconfig()[0]
    return None
