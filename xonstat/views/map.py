import logging
from pyramid.response import Response
from webhelpers.paginate import Page, PageURL
from xonstat.models import *
from xonstat.util import page_url

log = logging.getLogger(__name__)


def map_info(request):
    """
    List the information stored about a given map. 
    """
    map_id = request.matchdict['id']
    try:
        gmap = DBSession.query(Map).filter_by(map_id=map_id).one()
    except:
        gmap = None
    return {'gmap':gmap}
