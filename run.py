import threading
import logging
import signal

from iamcoin.api import app

threads = []

def start_api_server():
    app.run()


if __name__ == "__main__":
    logging.info("Start of the world")
    api_thread = threading.Thread(target=start_api_server, name="API-Thread")
    api_thread.start()

    threads.append(api_thread)

    for t in threads:
        t.join()
    logging.info("Adios:)")
