#!/usr/bin/env python
from flask import Flask, render_template, Response
import cv2
import sys
import numpy
from time import sleep

import threading
from queue import Queue


app = Flask(__name__)

cam_q = Queue(maxsize=5)

@app.route('/')
def index():
    return render_template('index.html')

# def gen():
#     i=1
#     while i<10:
#         yield (b'--frame\r\n'
#             b'Content-Type: text/plain\r\n\r\n'+str(i)+b'\r\n')
#         i+=1

def get_frame():

    camera_port=-1

    ramp_frames=100

    camera=cv2.VideoCapture(camera_port) #this makes a web cam object

    
    i=1
    while True:
        stringData = cam_q.get()
        yield (b'--frame\r\n'
            b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')
        i+=1
        sleep(0.25)

    del(camera)

@app.route('/calc')
def calc():
     return Response(get_frame(),mimetype='multipart/x-mixed-replace; boundary=frame')


def image_thread():
    retval, im = camera.read()
    imgencode=cv2.imencode('.jpg',im)[1]
    stringData=imgencode.tostring()
    cam_q.put(stringData,block=True)


if __name__ == '__main__':
    job_thread = threading.Thread(target=image_thread)
    job_thread.start()

    sleep(1)
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
