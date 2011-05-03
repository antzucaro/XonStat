import pyramid_jinja2
import sqlahelper
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from xonstat.models import initialize_db
from xonstat.views import * 

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # setup the database engine
    engine = engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.add_engine(engine)

    # initialize database structures
    initialize_db(engine)

    config = Configurator(settings=settings)

    config.add_renderer('.jinja2', pyramid_jinja2.renderer_factory)

    config.add_static_view('static', 'xonstat:static')

    config.add_route(name="main_index", pattern="/", view=main_index, 
            renderer='index.jinja2') 
    config.add_route(name="stats_submit", pattern="stats/submit", 
            view=stats_submit, renderer='index.jinja2') 

    return config.make_wsgi_app()
