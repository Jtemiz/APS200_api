import asyncio
import datetime
import logging
import socket
import socketserver
import threading
import time
import traceback
import app.globals as glob
from configparser import ConfigParser
from statistics import mode

config = ConfigParser()
config.read('app/preferences.ini')
UDP_SERVER_IP = config['arduino']['UDP_SERVER_IP']
UDP_SERVER_PORT = int(config['arduino']['UDP_SERVER_PORT'])
UDP_CLIENT_IP = config['arduino']['UDP_CLIENT_IP']
UDP_CLIENT_PORT = int(config['arduino']['UDP_CLIENT_PORT'])
logger = logging.getLogger()

ARD_COMMANDS = {
    'start': '070',
    'stop': '071',
    'reset': '072',
    'startKali': '073',
    'setKali': '074',
    'stopKali': '075'
}

def reset_arduino():
    try:
        send_message(ARD_COMMANDS['reset'])
        logger.info('arduino reset')
    except Exception as ex:
        logger.error(ex, exc_info=True)


def start_arduino():
    try:
        send_message(ARD_COMMANDS['start'])
        logger.info('arduino start')
    except Exception as ex:
        logger.error(ex, exc_info=True)


def stop_arduino():
    try:
        send_message(ARD_COMMANDS['stop'])
    except Exception as ex:
        logger.error(ex, exc_info=True)


def start_calibration():
    try:
        send_message(ARD_COMMANDS['startKali'])
        logger.info('arduino start cali')
    except Exception as ex:
        logger.error(ex, exc_info=True)


def start_calibration_distance_measuring():
    try:
        send_message(ARD_COMMANDS['reset'])
        send_message(ARD_COMMANDS['start'])
        logger.info('arduino start cali dist')
    except Exception as ex:
        logger.error(ex, exc_info=True)


def stop_calibration_distance_measuring():
    try:
        send_message(ARD_COMMANDS['stop'])
        logger.info('arduino stop cali dist')
    except Exception as ex:
        logger.error(ex, exc_info=True)


def stop_calibration():
    try:
        send_message(ARD_COMMANDS['stopKali'])
        logger.info('arduino stop cali')
    except Exception as ex:
        logger.error(ex, exc_info=True)


def abort_calibration():
    try:
        send_message(ARD_COMMANDS['stop'])
        logger.info('arduino abort cali')
    except Exception as ex:
        logger.error(ex, exc_info=True)


def set_calibration_value(value: int):
    try:
        send_message(ARD_COMMANDS['setKali'], value)
        logger.info('arduino set val')
    except Exception as ex:
        logger.error(ex, exc_info=True)


def send_message(message, value=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if value is None:
        msg = message
    else:
        msg = message + ';' + str(value)
    sock.sendto(msg.encode('ascii'), (UDP_CLIENT_IP, UDP_CLIENT_PORT))
    sock.close()


class MyUDPRequestHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        message = self.rfile.readline().strip().decode('UTF-8')
        if "VALUE" in message:
            typeDataSplit = message.split(";")
            data = {
                "position": float(typeDataSplit[1]),
                "height": float(typeDataSplit[2]),
                "speed": float(typeDataSplit[3]),
                "strWidth": glob.STREET_WIDTH,
                "limVal": glob.LIMIT_VALUE
            }
            glob.VIEW_VALUES.append(data)
            glob.LONGTERM_VALUES.append(data)
            glob.MEASUREMENT_DISTANCE = data["position"]
            if data["height"] > data["limVal"]:
                generate_beep()
        elif "STAT" in message:
            # STAT;Hoehe;Batterie;Boolean
            glob.WATCH_DOG = not glob.WATCH_DOG
            typeDataSplit = message.split(";")
            glob.MEASUREMENT_VALUE = float(typeDataSplit[2])
            glob.BATTERY_LEVEL_ENUM.append(float(typeDataSplit[3]))
            if len(glob.BATTERY_LEVEL_ENUM) > 20:
                glob.BATTERY_LEVEL_ENUM.pop(0)
            glob.BATTERY_LEVEL = mode(glob.BATTERY_LEVEL_ENUM)


# This class provides a multithreaded UDP server that can receive messages sent to the defined ip and port
class UDPServer(threading.Thread):
    server_address = (UDP_SERVER_IP, UDP_SERVER_PORT)
    udp_server_object = None

    def run(self):
        try:
            logger.info("RunUDPServer")
            self.udp_server_object = socketserver.ThreadingUDPServer(self.server_address, MyUDPRequestHandler)
            self.udp_server_object.serve_forever()
        except Exception as ex:
            logger.error(ex, exc_info=True)

    def stop(self):
        try:
            self.udp_server_object.shutdown()
        except Exception as ex:
            print(ex)
            logger.error(ex, exc_info=True)


class SUDPServer():
    __server: socketserver.ThreadingUDPServer = None

    @staticmethod
    def start_server():
        logger.info("StartSUDPServer")
        if SUDPServer.__server == None:
            SUDPServer()
            SUDPServer.__server.start()

    @staticmethod
    def stop_server():
        if SUDPServer.__server != None:
            SUDPServer.__server.stop()
            SUDPServer.__server = None

    def __init__(self):
        if SUDPServer.__server is not None:
            raise Exception("Class is already initialized")
        SUDPServer.__server = UDPServer()

def init_connection():
    try:
        SUDPServer.start_server()
    except Exception as ex:
        logger.error(ex, exc_info=True)
def generate_beep():
    try:
        from app.socket_handler import SIO
        asyncio.run(SIO.emit('beep'))
    except Exception as ex:
        logger.error(ex, exc_info=True)

