import logging
import random

def notfound(request):
    request.response.status = 404
    return {'rand': int(random.random() * 100)}
