import logging
from pyramid.response import Response
from sqlalchemy import desc
from webhelpers.paginate import Page, PageURL
from xonstat.models import *
from xonstat.util import page_url

log = logging.getLogger(__name__)

def map_index(request):
    """
    Provides a list of all the current maps. 
    """
    if 'page' in request.matchdict:
        current_page = request.matchdict['page']
    else:
        current_page = 1

    try:
        map_q = DBSession.query(Map).\
                order_by(Map.map_id.desc())

        maps = Page(map_q, current_page, url=page_url)

        
    except Exception as e:
        maps = None

    return {'maps':maps, }


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
