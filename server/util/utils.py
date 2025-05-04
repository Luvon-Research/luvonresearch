from uuid import uuid4
from datetime import datetime


def generate_uuid():
    return str(uuid4())

def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")