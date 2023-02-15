import datetime
import math
import random
import socket
import time
import asyncio
index = 0
height = 0
position = 0
speed = 0
height_median = 15
speed_max = 20

measurement_active = False
pause_active = False



def runServer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    global index
    while True:
        if index == 5:
            sock.sendto(bytes("STAT; " + str(datetime.datetime.now()), "ascii"), ("127.0.0.1", 5100))
        i += 1
                tmpstr = genMessage(i)
        print(tmpstr)
        sock.sendto(tmpstr, ("127.0.0.1", 5100))
        time.sleep(5)


def genMessage(index):
    str = "VALUE;{index};{position};{height};{speed}"
    changeVals()
    return bytes(str.format(index=index, position=position, height=height, speed=speed), 'ascii')


def changeVals():
    global height
    global position
    global speed
    position += 0.1
    if speed < speed_max:
        speed += round(random.random(), 2)
    else:
        speed -= round(random.random(), 2)
    height = round(math.sin(position), 2)



runServer()