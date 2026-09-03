"""Script diagnostico per HX711.
Stampa il valore raw e il valore in grammi ogni intervallo.
Eseguire da REPL: import hx711_diag
"""
import time
from loadcell import LoadCell


def run(interval_s=0.5):
    lc = LoadCell()
    print('HX711 diagnostic: Ctrl-C per uscire')
    try:
        while True:
            raw = lc.read_raw()
            grams = lc.get_weight_grams(n=3)
            print('raw:', raw, 'grams:', ('{:.2f}'.format(grams) if grams is not None else 'N/D'))
            time.sleep(interval_s)
    except KeyboardInterrupt:
        print('\nInterrotto dall\'utente')


if __name__ == '__main__':
    run()
