import threading
import logging
import signal
import time

from aiohttp import web
from multiprocessing import Process
from iamcoin.api import app

threads = []

class ServiceExit(Exception):
    pass

def service_shutdown(signum, frame):
    logging.info("Received signal...")
    raise ServiceExit

def start_api_server():
    try:
        web.run_app(app, port=5000)
    except ServiceExit:
        logging.info("Stopping API thread")

if __name__ == "__main__":
    logging.info("Start of the world")
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)
    start_api_server()
    #api_thread = threading.Thread(target=start_api_server, name="API-Thread")
    #api_thread.start()
    # api_process = Process(target= start_api_server, name="API-Thread")
    # api_process.start()
    #threads.append(api_thread)

    logging.info("Adios:)")
