from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from engineio.payload import Payload
from flask_apscheduler import APScheduler

# from redis import Redis
# from rq import Queue, Repeat

import json
import random
import numpy as np
from numpy.fft import fft2, ifft2, fftshift
from scipy.signal import convolve2d # Use SciPy's convolution
from typing import Tuple, Dict, Optional, Generator, Union

# from ca_tasks import perturb_ca

# def job_listener(event):
#     if not event.exception:
#         job = scheduler.get_job(event.job_id)
#         if job.name == "1":
#             print("wee")

# def perturb_ca(data):
#     print("hi")
#     # return data


def fft_convolve2d(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    2D convolution, using FFT
    """
    fr = fft2(x)
    fr2 = fft2(np.flipud(np.fliplr(y)))
    m,n = fr.shape
    cc = np.real(ifft2(fr*fr2))
    cc = np.roll(cc, - int(m / 2) + 1, axis=0)
    cc = np.roll(cc, - int(n / 2) + 1, axis=1)
    return cc

def parse_rule(rule: str) -> Tuple[List[int], List[int]]:
    """
    parses B/S rule strings
    """
    born = [int(i) for i in rule.split('/')[0][1:]]
    survive = [int(i) for i in rule.split('/')[1][1:]]
    return born, survive

# MODIFIED: Added 'boundary' argument
def automata(state: np.ndarray, rule: str = 'B3/S23', boundary: str = 'wrap') -> np.ndarray:
    """
    General cellular automata state transition function.

    Args:
        state (np.ndarray): The current board state (0s and 1s).
        rule (str): The ruleset string (e.g., 'B3/S23').
        boundary (str): Boundary condition for convolution.
                        'wrap' for periodic (toroidal),
                        'fill' for zero-padding.
                        Defaults to 'wrap'.

    Returns:
        np.ndarray: The next board state.
    """
    # Define the standard 3x3 Moore neighborhood kernel (excluding center)
    kernel = np.array([[1, 1, 1],
                       [1, 0, 1],
                       [1, 1, 1]])

    # Parse the rule string
    born_rules, survive_rules = parse_rule(rule)

    # Perform 2D convolution using SciPy
    # 'same' mode ensures output has the same shape as the input state
    # 'boundary' controls how edges are handled ('wrap' or 'fill')
    neighbor_sum = convolve2d(state, kernel, mode='same', boundary=boundary, fillvalue=0)

    # Apply the rules
    next_state: np.ndarray = np.zeros_like(state)

    # Apply survival rules (current cell is alive)
    for s_rule in survive_rules:
        next_state[(state == 1) & (neighbor_sum == s_rule)] = 1

    # Apply birth rules (current cell is dead)
    for b_rule in born_rules:
        next_state[(state == 0) & (neighbor_sum == b_rule)] = 1

    return next_state

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