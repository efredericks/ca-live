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

# def job_listener(event):
#     if not event.exception:
#         job = scheduler.get_job(event.job_id)
#         if job.name == "1":
#             print("wee")

# def perturb_ca(data):
#     print("hi")
#     # return data

class CA:
    def __init__(self, scheduler):
        self.data = np.random.random((80,120))
        self.scheduler = scheduler
        self.scheduler.add_job(func=self.perturb, id="generation", trigger='interval', seconds=2, misfire_grace_time=200, )

    def perturb(self):
        # print("ho")
        # for i in range(len(self.data)):
            # for j in range(len(self.data[i])):
                # self.data[i][j] = random.random()
        self.data = np.random.random((80, 120))
        # print(self.data[0][0])


    def listify(self):
        return self.data.tolist()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secr3t'

scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

Payload.max_decode_packets = 2048
socketio = SocketIO(app)

# queue = Queue(connection=Redis())
# data = np.random.random((80, 120))
# scheduler.add_job(func=perturb_ca, args=[data], id="1", trigger='interval', seconds=5, misfire_grace_time=200, )
cellular_automata = CA(scheduler=scheduler)

@app.route("/")
@app.route("/index")
def index():
    user = {'username': 'erik'}


    # job = queue.enqueue(perturb_ca, data, repeat=Repeat(times=20, interval=5))

    # data_list = data.tolist()
    data_list = cellular_automata.listify()#data.tolist()

    return render_template('index.html', user=user, data=json.dumps(data_list))

# socketio events
@socketio.on('user_connect')
def user_connected(msg):
    print(msg)

@socketio.on('disconnect')
def user_disconnected():
    print("User disconnected")

# @socketio.on('broadcast state')
# def broadcast_state(msg):
#     global cellular_automata
#     emit('data', {'data': msg['data']}, broadcast=True)

@socketio.on('tick_request')
def broadcast_tick():
    global cellular_automata
    emit('tick', {'data': json.dumps(cellular_automata.listify())})

if __name__ == "__main__":
    app.debug = True
    socketio.run(app)