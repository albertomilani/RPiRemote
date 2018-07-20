#!/usr/bin/env python

import select
import numpy
import socket
import sys
import os
import Queue

HOST_ADDRESS = 'localhost'
HOST_PORT = 10000

class CameraHandler():
    
    def __init__(self, camera):
        self.camera = camera

    def Capture(self, exp_time, gain):
        data = numpy.array(numpy.random.random((960,1280))*100,dtype=int)
        return data

    def TestMsg(self):
        return 't0p4'

# Global variables
exp_time = 1000 # microseconds
gain = 150 # range 0-300

def readCaptureParams():

    global exp_time
    global gain

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock..bind((HOST_ADDRESS, HOST_PORT))
    sock.listen(1)


