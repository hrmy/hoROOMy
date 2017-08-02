# Импортим все нужное, прописанное в __all__
from . import *

def parse(**kwargs):
    print('Example parser started with kwargs:', kwargs)
    yield {'cost': 1234}