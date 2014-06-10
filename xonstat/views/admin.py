from pyramid.response import Response
from pyramid.httpexceptions import HTTPForbidden

def forbidden(request):
    '''A simple forbidden view. Does nothing more than set the status and then
    gets the heck out of dodge. The forbidden.mako template does the work.'''
    request.response.status = 403
    return {}
