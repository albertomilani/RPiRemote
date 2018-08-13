#!/usr/bin/env python

import numpy
import socket
import sys
import os
import threading
import time
import zwoasi as asi
import json
from syslog import *

# exit codes
EC_CAMERA_NOT_FOUND = 100
EC_GENERIC_ERROR = 110

# network params
HOST_ADDRESS = '0.0.0.0'
HOST_PORT = 10000

# CCD global variables
exp_time = 500 # microseconds
gain = 100 # range 0-300

class CameraHandler():
    
    def __init__(self, camera):
        self.camera = camera

    def FakeCapture(self, exposure_time, gain_value):
        # example data
        data = numpy.array(numpy.random.random((960,1280))*100,dtype=numpy.uint8)
        return data

    def Capture(self, exposure_time, gain_value):

        # Use minimum USB bandwidth permitted
        self.camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, self.camera.get_controls()['BandWidth']['MinValue'])

        self.camera.set_control_value(asi.ASI_GAIN, gain_value) # range 0-300
        self.camera.set_control_value(asi.ASI_EXPOSURE, exposure_time) # microsecond
        self.camera.set_control_value(asi.ASI_WB_B, 99)
        self.camera.set_control_value(asi.ASI_WB_R, 75)
        self.camera.set_control_value(asi.ASI_GAMMA, 50)
        self.camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
        self.camera.set_control_value(asi.ASI_FLIP, 0)
        #self.camera.set_roi(bins=2)
        self.camera.set_image_type(asi.ASI_IMG_RAW8)

        try:
            # Force any single exposure to be halted
            self.camera.stop_video_capture()
            self.camera.stop_exposure()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            pass

        return self.camera.capture()


def readCaptureParams():
    global exp_time
    global gain
    data = conn.recv(4096)
    if data:
        print data
        params = json.loads(data)
        exp_time = params['exp_time']
        gain = params['gain']

def captureAndSend(camera):

    ccd = CameraHandler(camera)
    print(exp_time, gain)
    image = ccd.Capture(exp_time, gain);
    #image = ccd.FakeCapture(exp_time, gain);
    im_bytes = image.tobytes()

    chunk_size = 1024
    msg_len = len(im_bytes)
    #print msg_len

    for i in xrange((msg_len/chunk_size)+1):
        start = i * chunk_size
        end = start + chunk_size
        if end > msg_len:
            end = msg_len
        conn.sendall(im_bytes[start:end])

if __name__ == "__main__":
    
    syslog(LOG_INFO, 'Start server')

    libasi_path = '/opt/ASI_SDK/lib/armv7/libASICamera2.so'
    asi.init(libasi_path)

    try:
        camera0 = asi.Camera(0)
        syslog(LOG_INFO, 'Camera found')
    except:
        syslog(LOG_ERR, 'Camera not found')
        sys.exit(EC_CAMERA_NOT_FOUND)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        sock.bind((HOST_ADDRESS, HOST_PORT))
        sock.listen(2)
        
        syslog(LOG_INFO, 'Waiting connections...')

        while True:
            conn, addr = sock.accept()
            thread1 = threading.Thread( target=readCaptureParams, args=() )
            thread2 = threading.Thread( target=captureAndSend, args=(camera0,) )

            thread1.start()
            thread2.start()

            thread1.join()
            thread2.join()

            conn.close()

    except:
        sock.close()
        syslog(LOG_ERR, 'Generic error')
        sys.exit(EC_GENERIC_ERROR)

    sock.close()

