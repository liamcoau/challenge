from __future__ import absolute_import

from celery import Celery

BROKER = "mongodb://localhost:27017/files"

BACKEND = "mongodb://localhost:27017/"

app = Celery("lib", broker=BROKER, backend=BACKEND, include=["lib.tasks"])

app.config_from_object("lib.celeryconfig")

if __name__ == "__main__":
    print("This file is only for use by celery, do not attempt to run it.")
