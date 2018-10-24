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

def get_frame():
    i=1
    while True:
        stringData = cam_q.get(block=True)
        print("size of queue: %d" % cam_q.qsize() )
        yield (b'--frame\r\n'
            b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')
        i+=1
        

@app.route('/calc')
def calc():
     return Response(get_frame(),mimetype='multipart/x-mixed-replace; boundary=frame')


def image_thread():
    camera_port=-1

    ramp_frames=100

    camera=cv2.VideoCapture(camera_port) #this makes a web cam object
    while True:
        try:
            print("Snapping a photo!")
            retval, im = camera.read()
            imgencode=cv2.imencode('.jpg',im)[1]
            stringData=imgencode.tostring()
            cam_q.put(stringData,block=True)
            sleep(0.05)
        except Exception as e:
            print("Exception taking photo: %s" % str(e) )
            # sleep(0.5)


if __name__ == '__main__':
    job_thread = threading.Thread(target=image_thread)
    job_thread.start()

    sleep(1)
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
