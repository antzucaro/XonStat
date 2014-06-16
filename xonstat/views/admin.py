from pyramid.response import Response
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from pyramid.security import remember, forget
from pyramid_persona.views import verify_login
from xonstat.models import *

def forbidden(request):
    '''A simple forbidden view. Does nothing more than set the status and then
    gets the heck out of dodge. The forbidden.mako template does the work.'''
    request.response.status = 403
    return {}

def login(request):
    # Verify the assertion and get the email of the user
    persona_email = verify_login(request)

    # Check that the email exists in the players table
    player_email = DBSession.query(Player).\
            filter(Player.email_addr == persona_email).one()

    log.debug("Verified email address: %s" % persona_email)
    log.debug("Corresponding player is %s" % player_email)

    if player_email is not None:
        # Add the headers required to remember the user to the response
        request.response.headers.extend(remember(request, persona_email))
    else:
        url = request.route_url("forbidden")
        return HTTPFound(location=url)

    # Return a json message containing the address or path to redirect to.
    return {'redirect': request.POST['came_from'], 'success': True}

def merge(request):
    '''A simple merge view. The merge.mako template does the work.'''
    return {}
