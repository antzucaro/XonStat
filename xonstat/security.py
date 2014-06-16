from pyramid.security import Allow, Everyone

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
        (Allow, Everyone, 'view'),
        (Allow, 'group:admins', 'merge')
    ]
    def __init__(self, request):
        pass


def groupfinder(userid, request):
    print('userid is %s' % userid)
    if userid in USERS:
        return GROUPS.get(userid, [])
    else:
        return []
