from button import Button
import time


def run(interval_s=0.1):
    b = Button()
    print('Button test — Ctrl-C per uscire')
    last_deb = False
    try:
        while True:
            raw = b._raw_pressed()
            deb = b.is_pressed()
            print('raw:', raw, 'debounced:', deb)
            if deb and not last_deb:
                print('>> Press detected')
            last_deb = deb
            time.sleep(interval_s)
    except KeyboardInterrupt:
        print('\nTest interrotto')


if __name__ == '__main__':
    run()
