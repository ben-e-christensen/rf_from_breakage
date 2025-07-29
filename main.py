import time
import threading
from rf_acquisition import acquisition_thread

def main():
    thread = threading.Thread(target=acquisition_thread)
    thread.daemon = True
    thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == "__main__":
    main()
