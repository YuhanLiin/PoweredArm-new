from enum import Enum
from datetime import datetime

class Gesture(Enum):
    rest = 0
    open = 1
    grip = 2
    key = 3

def dated_name(stem):
    return '{}-{:%Y-%m-%d-%H-%M-%S}'.format(stem, datetime.today())
