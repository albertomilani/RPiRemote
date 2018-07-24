#!/usr/bin/env python

import numpy
import socket
import sys
import os
import threading
import time
import zwoasi as asi

HOST_ADDRESS = '0.0.0.0'
HOST_PORT = 10000

# CCD global variables
exp_time = 1000 # microseconds
gain = 150 # range 0-300

class CameraHandler():
    
    def __init__(self, camera):
        self.camera = camera

    def Capture(self, exposure_time, gain_value):
        # example data
        #data = numpy.array(numpy.random.random((960,1280))*100,dtype=numpy.uint8)
        #return data

        # Use minimum USB bandwidth permitted
        self.camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, self.camera.get_controls()['BandWidth']['MinValue'])

        self.camera.set_control_value(asi.ASI_GAIN, gain_value) # range 0-300
        self.camera.set_control_value(asi.ASI_EXPOSURE, exposure_time) # microsecond
        self.camera.set_control_value(asi.ASI_WB_B, 99)
        self.camera.set_control_value(asi.ASI_WB_R, 75)
        self.camera.set_control_value(asi.ASI_GAMMA, 50)
        self.camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
        self.camera.set_control_value(asi.ASI_FLIP, 0)
        self.camera.set_roi(bins=2)
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
    return
    while True:
        data = conn.recv(1024)
        print(data)


def captureAndSend(camera):

    ccd = CameraHandler(camera)

    image = ccd.Capture(exp_time, gain);
    print image
    im_bytes = image.tobytes()

    chunk_size = 1024
    msg_len = len(im_bytes)
    print msg_len

    for i in xrange((msg_len/chunk_size)+1):
        start = i * chunk_size
        end = start + chunk_size
        if end > msg_len:
            end = msg_len
        conn.sendall(im_bytes[start:end])

if __name__ == "__main__":

    libasi_path = '/opt/ASI_SDK/lib/armv7/libASICamera2.so'
    asi.init(libasi_path)

    camera0 = asi.Camera(0)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #sock.setblocking(0)
    sock.bind((HOST_ADDRESS, HOST_PORT))
    sock.listen(2)

    while True:
        conn, addr = sock.accept()
        thread1 = threading.Thread( target=readCaptureParams, args=() )
        thread2 = threading.Thread( target=captureAndSend, args=(camera0,) )

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()
        break


    sock.close()

