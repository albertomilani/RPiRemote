#!/usr/bin/env python

import socket
import sys
import threading
import time

HOST_ADDRESS = 'localhost'
HOST_PORT = 10000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def sendCaptureParams():
    print('Send params')
    while True:
        sock.sendall('cazzolo')
        time.sleep(0.02)

def receiveImage():
    print('Receive image')
    while True:
        data = sock.recv(1024)
        print data

sock.connect((HOST_ADDRESS, HOST_PORT))

th1 = threading.Thread( target=sendCaptureParams, args=() )
th2 = threading.Thread( target=receiveImage, args=() )

th1.start()
th2.start()

th1.join()
th2.join()

sock.close()

