import logging
import random

def notfound(request):
    return {'rand': int(random.random() * 100)}
