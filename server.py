#!/usr/bin/env python

import numpy
import socket
import sys
import os
import threading
import time

HOST_ADDRESS = 'localhost'
HOST_PORT = 10000

# CCD global variables
exp_time = 1000 # microseconds
gain = 150 # range 0-300

class CameraHandler():
    
    def __init__(self, camera):
        self.camera = camera

    def Capture(self, exposure_time, gain_value):
        data = numpy.array(numpy.random.random((960,1280))*100,dtype=int)
        return data

    def TestMsg(self):
        return 't0p4'

def readCaptureParams():

    global exp_time
    global gain

    print('Start reading')

    while True:
        data = conn.recv(1024)
        print(data)


def captureAndSend():

    ccd = CameraHandler(None)

    print('Start writing')

    while True:
        #image = ccd.Capture(exp_time, gain)
        msg = ccd.TestMsg()
        conn.sendall(msg)
        time.sleep(0.0333)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST_ADDRESS, HOST_PORT))
sock.listen(2)

while True:
    conn, addr = sock.accept()
    thread1 = threading.Thread( target=readCaptureParams, args=() )
    thread2 = threading.Thread( target=captureAndSend, args=() )

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()


sock.close()

