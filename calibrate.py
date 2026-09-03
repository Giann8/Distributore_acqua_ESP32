"""Script da eseguire UNA TANTUM (manualmente, non fa parte del boot
automatico) per calcolare offset e scale_factor della cella di carico.
Al termine, copia i valori stampati in config.py (HX711_OFFSET,
HX711_SCALE_FACTOR)."""

import time
from loadcell import LoadCell

KNOWN_WEIGHT_G = 500  # <-- cambia con il peso esatto del tuo oggetto di riferimento

loadcell = LoadCell()

print("=== FASE 1: TARA ===")
print("Assicurati che la piattaforma sia VUOTA.")
print("Calibrazione tra 3 secondi...")
time.sleep(3)

offset = loadcell.read_average(20)
print("Offset (zero):", offset)

print("\n=== FASE 2: CALIBRAZIONE ===")
print("Metti un peso noto di", KNOWN_WEIGHT_G, "g sulla piattaforma.")
print("Calibrazione tra 5 secondi...")
time.sleep(5)

raw_with_weight = loadcell.read_average(20)
print("Valore raw con peso:", raw_with_weight)

scale_factor = (raw_with_weight - offset) / KNOWN_WEIGHT_G
print("Fattore di scala (raw per grammo):", scale_factor)

print("\n=== CALIBRAZIONE COMPLETATA ===")
print("Valori calcolati (verranno salvati automaticamente in config.py):")
print("HX711_OFFSET =", offset)
print("HX711_SCALE_FACTOR =", scale_factor)

# Applica subito i valori per il test in tempo reale
loadcell.offset = offset
loadcell.scale_factor = scale_factor

# Salva automaticamente i valori calcolati in config.py per evitare
# di doverli copiare manualmente ogni volta. Se config.py non contiene
# le variabili, verranno aggiunte. Va fatto PRIMA del loop di test
# manuale qui sotto: quel loop e' bloccante e termina solo con Ctrl+C.
try:
    cfg_path = 'config.py'
    with open(cfg_path, 'r') as f:
        lines = f.readlines()

    found_offset = False
    found_scale = False
    for i, l in enumerate(lines):
        if l.strip().startswith('HX711_OFFSET'):
            lines[i] = 'HX711_OFFSET = {}\n'.format(offset)
            found_offset = True
        if l.strip().startswith('HX711_SCALE_FACTOR'):
            lines[i] = 'HX711_SCALE_FACTOR = {}\n'.format(scale_factor)
            found_scale = True

    if not found_offset:
        # inserisci vicino alla cima del file: dopo i pin HX711 se presenti
        insert_at = 0
        for i, l in enumerate(lines):
            if l.strip().startswith('# Valori di calibrazione'):
                insert_at = i + 1
                break
        lines.insert(insert_at, 'HX711_OFFSET = {}\n'.format(offset))

    if not found_scale:
        # prova a inserire dopo offset
        insert_at = 0
        for i, l in enumerate(lines):
            if l.strip().startswith('HX711_OFFSET'):
                insert_at = i + 1
                break
        lines.insert(insert_at, 'HX711_SCALE_FACTOR = {}\n'.format(scale_factor))

    with open(cfg_path, 'w') as f:
        f.writelines(lines)

    print('\nValori di calibrazione salvati in', cfg_path)
    print('HX711_OFFSET =', offset)
    print('HX711_SCALE_FACTOR =', scale_factor)
except Exception as e:
    print('Impossibile salvare in config.py:', e)

print("\n=== TEST LETTURA IN GRAMMI (Ctrl+C per fermare) ===")
print("Togli il peso noto per vedere se torna vicino a 0g.")
time.sleep(3)

try:
    while True:
        grams = loadcell.get_weight_grams(n=5)
        if grams is not None:
            print("Peso: {:.1f} g".format(grams))
        else:
            print("Errore lettura HX711")
        time.sleep(0.3)
except KeyboardInterrupt:
    print('\nTest interrotto dall\'utente')
