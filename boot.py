import config

if config.DEV_MODE:
    print("=== MODALITA' SVILUPPO ATTIVA (config.DEV_MODE = True) ===")
    print("boot.py salta connessione WiFi e WebREPL.")
elif not config.WIFI_ENABLED:
    print("WiFi disattivato (config.WIFI_ENABLED = False), avvio offline.")
else:
    import wifi

    connected, ip = wifi.connect()

    if connected:
        print("WiFi connesso, IP:", ip)
        # WebREPL richiede una connessione attiva: lo avviamo solo ora,
        # cosi' non tenta nemmeno il bind se la rete non e' disponibile.
        try:
            import webrepl
            webrepl.start()
        except Exception as e:
            print("WebREPL non avviato:", e)
            print("Per configurarlo, da REPL: import webrepl_setup")
    else:
        print("WiFi non connesso, avvio in modalita offline (nessun WebREPL).")