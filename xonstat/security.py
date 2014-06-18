import logging
from pyramid.security import Allow, Everyone
from xonstat.models import DBSession, Player, PlayerGroups

log = logging.getLogger(__name__)

USERS = {
    'admin':'admin',
    'viewer':'viewer',
}

GROUPS = {
    'admin':['group:admins'],
}

# default ACL
class ACLFactory(object):
    __acl__ = [
        # permission, principal, permission
        (Allow, Everyone, 'view'),
        (Allow, 'admin', 'merge')
    ]
    def __init__(self, request):
        pass


def groupfinder(userid, request):
    groups = []
    try:
        groups_q = DBSession.query(PlayerGroups.group_name).\
            filter(Player.email_addr == userid).all()

        for g in groups_q:
            groups.append(g.group_name)
    except:
        pass

    return groups
