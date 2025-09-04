from flask import Flask, render_template
import json
import random
import numpy as np

app = Flask(__name__)

data = np.random.random((80, 120))

@app.route("/")
@app.route("/index")
def index():
    user = {'username': 'erik'}

    data_list = data.tolist()

    return render_template('index.html', user=user, data=json.dumps(data_list))