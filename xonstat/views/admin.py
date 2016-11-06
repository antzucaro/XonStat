from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.session import check_csrf_token
from pyramid_persona.views import verify_login
from xonstat.models import DBSession, Player


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

    #log.debug("Verified email address: %s" % persona_email)
    #log.debug("Corresponding player is %s" % player_email)

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
    s = DBSession()

    # only do a merge if we have all of the required data
    if request.params.has_key("csrf_token"):
        # check the token to prevent request forgery
        st = request.session.get_csrf_token()
        check_csrf_token(request)

        if request.params.has_key("w_pid") and request.params.has_key("l_pid"):
            w_pid = request.params.get("w_pid")
            l_pid = request.params.get("l_pid")

            # do the merge, hope for the best!
            try:
                s.execute("select merge_players(:w_pid, :l_pid)",
                    {"w_pid": w_pid, "l_pid": l_pid})

                s.commit()

                request.session.flash(
                    "Successfully merged player %s into %s!" % (l_pid, w_pid),
                    "success")

            except:
                s.rollback()

                request.session.flash(
                    "Could not merge player %s into %s." % (l_pid, w_pid),
                    "failure")

    return {}
