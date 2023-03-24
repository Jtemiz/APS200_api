import datetime
import math
import random
import signal
import socket
import socketserver
import threading
import time
import asyncio
from threading import Thread

index = 0
height = 0
position = 0
speed = 0
height_median = 15
speed_max = 20
battery = 100

measurement_active = False
pause_active = False
calibration_active = True

def runServer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    global index
    while True:
        if index % 5 == 0:
            msg = genStatus(index)
            sock.sendto(msg, ("127.0.0.1", 5100))
        index += 1
        if measurement_active:
            tmpstr = genMessage()
            print(tmpstr)
            sock.sendto(tmpstr, ("127.0.0.1", 5100))
        time.sleep(0.2)


def genMessage():
    str = "VALUE;{position};{height};{speed}"
    changeVals()
    return bytes(str.format(position=position, height=height, speed=speed), 'ascii')

def genStatus(index):
    str = "STAT;{index};{height};{battery};{measurementActive}"
    changeVals()
    return bytes(str.format(index=index, height=height, battery=battery, measurementActive=measurement_active), 'ascii')

def changeVals():
    global height
    global position
    global speed
    global battery
    position = round(position + 0.1, 2)
    if speed < speed_max:
        speed = round(speed + random.random(), 2)
    else:
        speed = round(speed - random.random(), 2)
    height = round(math.sin(position) * 5, 2)
    if battery < 1:
        battery = 100
    else:
        battery = round(battery - 1, 2)


class UDPMessageHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        data = self.rfile.readline().strip().decode('UTF-8')
        print(data)
        global measurement_active
        global position
        global calibration_active
        if data == '070':
            measurement_active = True
        elif data == '071':
            measurement_active = False
        elif data == '072':
            position = 0
        elif data == '073':
            calibration_active = False
        elif data == '074':
            if calibration_active:
                print(data, 'check')
        elif data == '075':
            calibration_active = False

class UDPServer(threading.Thread):
    server_address = ("127.0.0.1", 9000)
    udp_server_object = None

    def run(self):
        try:
            self.udp_server_object = socketserver.ThreadingUDPServer(self.server_address, UDPMessageHandler)
            self.udp_server_object.serve_forever()
        except Exception as ex:
            print(ex)

    def stop(self):
        try:
            self.udp_server_object.shutdown()
            self.udp_server_object = None
        except Exception as ex:
            print(ex)


def run():
    UDPServer().start()
    thread = Thread(target=runServer())
    thread.start()


run()
