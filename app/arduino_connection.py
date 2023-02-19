import logging
import socket
import socketserver
import threading
import traceback
import app.globals as glob
from configparser import ConfigParser

config = ConfigParser()
config.read('app/preferences.ini')
UDP_SERVER_IP = config['arduino']['UDP_SERVER_IP']
UDP_SERVER_PORT = int(config['arduino']['UDP_SERVER_PORT'])
UDP_CLIENT_IP = config['arduino']['UDP_CLIENT_IP']
UDP_CLIENT_PORT = int(config['arduino']['UDP_CLIENT_PORT'])

ARD_COMMANDS = {
    'start': '070',
    'stop': '071',
    'reset': '072',
    'startKali': '073'
}


def start_arduino():
    try:
        send_message(ARD_COMMANDS['start'])
    except Exception as ex:
        print(ex)


def send_message(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, (UDP_CLIENT_IP, UDP_CLIENT_PORT))
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
        elif "STAT" in message:
            # STAT;Hoehe;Batterie;Boolean
            typeDataSplit = message.split(";")
            glob.HEIGHT = float(typeDataSplit[1])
            glob.BATTERY_LEVEL = float(typeDataSplit[2])
            # todo reintegrate stop measuring when battery too low


# This class provides a multithreaded UDP server that can receive messages sent to the defined ip and port
class UDPServer(threading.Thread):
    server_address = (UDP_SERVER_IP, UDP_SERVER_PORT)
    udp_server_object = None

    def run(self):
        try:
            logging.info("RunUDPServer")
            self.udp_server_object = socketserver.ThreadingUDPServer(self.server_address, MyUDPRequestHandler)
            self.udp_server_object.serve_forever()
        except Exception as ex:
            logging.error("UDPServer.run(): " + str(ex) + "\n" + traceback.format_exc())

    def stop(self):
        try:
            self.udp_server_object.shutdown()
        except Exception as ex:
            logging.error("UDPServer.stop(): " + str(ex) + "\n" + traceback.format_exc())


class SUDPServer():
    __server: socketserver.ThreadingUDPServer = None

    @staticmethod
    def start_server():
        logging.info("StartSUDPServer")
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
        print(ex)
