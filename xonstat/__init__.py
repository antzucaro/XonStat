import sqlahelper
from pyramid.config import Configurator
from sqlalchemy import engine_from_config


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # setup the database engine
    engine = engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.add_engine(engine)

    # create the database structures
    # note: have to import here else we'll get` 
    # "no engine 'default' was configured
    from xonstat.models import initialize_sql
    initialize_sql(engine)

    config = Configurator(settings=settings)
    config.add_static_view('static', 'xonstat:static')
    return config.make_wsgi_app()


