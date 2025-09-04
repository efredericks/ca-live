# ca-live

Flask server for live cellular automata interaction.

## To run:

1. Install redis
2. Install Python requirements
3. Run redis server: `redis-server`
4. Run Flask app:
  1. `FLASK_APP=ca_main.py`
  2. `python3 -m flask run`
5. Run rq worker: `rq worker --with-scheduler`