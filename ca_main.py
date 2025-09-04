from flask import Flask, render_template
from redis import Redis
from rq import Queue, Repeat

import json
import random
import numpy as np

from ca_tasks import perturb_ca

app = Flask(__name__)

queue = Queue(connection=Redis())

data = np.random.random((80, 120))

@app.route("/")
@app.route("/index")
def index():
    user = {'username': 'erik'}


    queue.enqueue(perturb_ca, data, repeat=Repeat(times=20, interval=5))
    data_list = data.tolist()

    return render_template('index.html', user=user, data=json.dumps(data_list))