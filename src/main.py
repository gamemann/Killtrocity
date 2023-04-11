import killfrenzy
import kilimanjaro

import time
import threading

def kf_init():
    killfrenzy.init()

def km_init():
    kilimanjaro.init()

def main():
    p1 = threading.Thread(target=kf_init)
    p2 = threading.Thread(target=km_init)

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()