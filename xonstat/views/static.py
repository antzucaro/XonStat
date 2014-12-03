import os
from pyramid.response import FileResponse

def robots(request):
    here = os.path.dirname(__file__)
    robots_txt = os.path.join(here, "../static", "robots.txt")
    return FileResponse(robots_txt, request=request)
