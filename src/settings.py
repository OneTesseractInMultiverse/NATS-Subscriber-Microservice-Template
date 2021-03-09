import os

NATS_SERVER: str = os.environ.get('NATS_SERVER')
NATS_SUBJECT: str = os.environ.get('NATS_SUBJECT')
NATS_QUEUE: str = os.environ.get('NATS_QUEUE')
