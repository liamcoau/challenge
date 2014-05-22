from __future__ import absolute_import

from celery import Celery

BROKER = "mongodb://localhost:27017/files"
BACKEND = "mongodb://localhost:27017/"

app = Celery("lib", broker=BROKER, backend=BACKEND, include=["lib.tasks"])

app.config_from_object("lib.celeryconfig")
