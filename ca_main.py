from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from engineio.payload import Payload
from flask_apscheduler import APScheduler

# from redis import Redis
# from rq import Queue, Repeat

import json
import random
import numpy as np

# from ca_tasks import perturb_ca

def perturb_ca(data):
    print("hi")
    # return data

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secr3t'

scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

Payload.max_decode_packets = 2048

# queue = Queue(connection=Redis())

data = np.random.random((80, 120))

scheduler.add_job(func=perturb_ca, args=[data], id="1", trigger='interval', seconds=5, misfire_grace_time=200, )

@app.route("/")
@app.route("/index")
def index():
    user = {'username': 'erik'}


    # job = queue.enqueue(perturb_ca, data, repeat=Repeat(times=20, interval=5))

    data_list = data.tolist()

    return render_template('index.html', user=user, data=json.dumps(data_list))

if __name__ == "__main__":
    app.debug = True
    socketio.run(app)