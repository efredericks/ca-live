import sys

from redis import Redis
from rq import Worker

worker = Worker(['default'], connection=Redis())
worker.work()