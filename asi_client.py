#!/usr/bin/env python

import Tkinter
import time
import threading
import random
import Queue
import numpy as np
import socket
import sys
import json
from PIL import Image, ImageTk
import traceback
import struct

CONFIG_FILE = './asi_client.conf'

# ASI config
ASI_ADDRESS = 'localhost'
ASI_PORT = 10001
ASI_X = 1280
ASI_Y = 960
ASI_IMG_SIZE = ASI_X * ASI_Y

# millisec
MIN_EXP_TIME = 1
MAX_EXP_TIME = 15000
DEFAULT_EXP_TIME = 20

SOCKET_TIMEOUT = 20

class GuiPart:
    def __init__(self, master, queue, endCommand):

        with open(CONFIG_FILE) as f:
            self.config = json.load(f)

        self.master = master
        self.queue = queue

        self.master.title("ASI client")
        self.master.geometry("630x600")

        self.master.protocol("WM_DELETE_WINDOW", endCommand)


        self.frame_img = Tkinter.Frame(self.master)
        self.frame_img.grid(row=0, column=0)

        self.canvas = Tkinter.Canvas(self.frame_img, width=600, height=450)
        self.canvas.grid(row=0, column=0, rowspan=2, sticky="N")
       
        self.slider_exp = Tkinter.Scale(self.frame_img, from_=MIN_EXP_TIME, to=MAX_EXP_TIME, resolution=10, length=580, orient=Tkinter.HORIZONTAL, variable=exp_time, label='Exp time (ms)')
        self.slider_exp.set(DEFAULT_EXP_TIME)
        self.slider_exp.grid(row=1, column=0)

        self.slider_gain = Tkinter.Scale(self.frame_img, from_=0, to=300, length=580, orient=Tkinter.HORIZONTAL, variable=gain, label='Gain')
        self.slider_gain.set(150)
        self.slider_gain.grid(row=2, column=0)

        self.frame_ch = Tkinter.Frame(self.frame_img)
        self.frame_ch.grid(row=3, column=0)

        self.crosshair_x_label = Tkinter.Label(self.frame_ch, text='Crosshair: x')
        self.crosshair_x_label.grid(row=0, column=0, sticky="W")
        self.crosshair_x = Tkinter.Entry(self.frame_ch)
        self.crosshair_x.insert(0, self.config['crosshair'][0])
        self.crosshair_x.grid(row=0, column=1, sticky="W")

        self.crosshair_y_label = Tkinter.Label(self.frame_ch, text='y')
        self.crosshair_y_label.grid(row=0, column=2, sticky="W")
        self.crosshair_y = Tkinter.Entry(self.frame_ch)
        self.crosshair_y.insert(0, self.config['crosshair'][1])
        self.crosshair_y.grid(row=0, column=3, sticky="W")

        self.canvas_image = None

    def processIncomingImage(self, msg):

        data = msg['image']

        if self.canvas_image is not None:
            self.canvas.delete(self.canvas_image)
        self.im = Image.frombytes('L', (data.shape[1],data.shape[0]), data.astype('b').tostring()).resize((853,640))
        self.photo = ImageTk.PhotoImage(image=self.im)
        self.canvas.delete('all')
        self.canvas_image = self.canvas.create_image(0,0,image=self.photo,anchor=Tkinter.NW)

        # draw crosshair
        try:
            x = int(self.crosshair_x.get())
        except ValueError:
            x = 0
        try:
            y = int(self.crosshair_y.get())
        except ValueError:
            y = 0

        self.canvas.create_line(x, 0, x, y-10, fill='red', width=1)
        self.canvas.create_line(x, y+10, x, 640, fill='red', width=1)

        self.canvas.create_line(0, y, x-10, y, fill='red', width=1)
        self.canvas.create_line(x+10, y, 853, y, fill='red', width=1)

        self.config['crosshair'][0] = self.crosshair_x.get()
        self.config['crosshair'][1] = self.crosshair_y.get()

        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)

    def processIncoming(self):
        while self.queue.qsize():
            try:
                self.msg = self.queue.get(0)

                if self.msg['type'] == 'image':
                    self.processIncomingImage(self.msg)

            except Queue.Empty:
                pass

class ThreadedClient:
   
    def __init__(self, master):

        self.master = master

        self.queue = Queue.Queue()

        self.gui = GuiPart(master, self.queue, self.endApplication)

        self.running = 1

        self.thread_img = threading.Thread(target=self.getRemoteImage)
        self.thread_img.start()

        self.periodicCall()

    def periodicCall(self):
        self.gui.processIncoming()
        if not self.running:
            sys.exit(1)
        self.master.after(100, self.periodicCall)

    def getRemoteImage(self):
        while self.running:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            sock.connect((ASI_ADDRESS, ASI_PORT))

            # send capture parameters
            params = {}
            params['exp_time'] = 1000*exp_time.get()
            params['gain'] = gain.get()
            sock.sendall(json.dumps(params))

            # receive capture
            arr = b''
            time_start = time.time()
            try:
                while len(arr) < ASI_IMG_SIZE:
                    now = time.time()
                    if (now - time_start) > SOCKET_TIMEOUT:
                        break
                    data  = sock.recv(2**16)
                    if data:
                        arr += data
                image_array = np.frombuffer(arr, dtype=np.dtype(np.uint8)).reshape((ASI_Y, ASI_X))
                sock.close()
                msg = {'type':'image', 'image':image_array}
                self.queue.put(msg)
            except:
                traceback.print_exc()
                pass

    def endApplication(self):
        self.running = 0

root = Tkinter.Tk()

exp_time = Tkinter.IntVar()
gain = Tkinter.IntVar()

client = ThreadedClient(root)
root.mainloop()
