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

    # ROOT ROUTE
    config.add_route("main_index", "/")
    config.add_view(main_index, route_name="main_index",
        renderer="main_index.mako")

    # PLAYER ROUTES
    config.add_route("player_game_index_default",
            "/player/{player_id:\d+}/games")
    config.add_view(player_game_index, route_name="player_game_index_default",
        renderer="player_game_index.mako")

    config.add_route("player_game_index",
            "/player/{player_id:\d+}/games/page/{page:\d+}")
    config.add_view(player_game_index, renderer="player_game_index.mako")

    config.add_route("player_index_paged", "/players/page/{page:\d+}")
    config.add_view(player_index, route_name="player_index_paged",
        renderer="player_index.mako")

    config.add_route("player_index", "/players")
    config.add_view(player_index, route_name="player_index",
        renderer="player_index.mako")

    config.add_route("player_info", "/player/{id:\d+}")
    config.add_view(player_info, route_name="player_info",
        renderer="player_info.mako")

    # GAME ROUTES
    config.add_route("game_index", "/games")
    config.add_view(game_index, route_name="game_index",
        renderer="game_index.mako")

    config.add_route("game_index_paged", "/games/page/{page:\d+}")
    config.add_view(game_index, route_name="game_index_paged",
        renderer="game_index.mako")

    config.add_route("game_info", "/game/{id:\d+}")
    config.add_view(game_info, route_name="game_info",
        renderer="game_info.mako")

    # SERVER ROUTES
    config.add_route("server_index_paged", "/servers/page/{page:\d+}")
    config.add_view(server_index, route_name="server_index_paged",
        renderer="server_index.mako")

    config.add_route("server_index", "/servers")
    config.add_view(server_index, route_name="server_index",
        renderer="server_index.mako")

    config.add_route("server_game_index",
        "/server/{server_id:\d+}/games/page/{page:\d+}")
    config.add_view(server_game_index, route_name="server_game_index",
        renderer="server_game_index.mako")

    config.add_route("server_info", "/server/{id:\d+}")
    config.add_view(server_info, route_name="server_info",
        renderer="server_info.mako")

    # MAP ROUTES
    config.add_route("map_index_paged", "/maps/page/{page:\d+}")
    config.add_view(map_index, route_name="map_index_paged",
        renderer="map_index.mako")

    config.add_route("map_index", "/maps")
    config.add_view(map_index, route_name="map_index",
        renderer="map_index.mako")

    config.add_route("map_info", "/map/{id:\d+}")
    config.add_view(map_info, route_name="map_info",
        renderer="map_info.mako")

    config.add_route("stats_submit", "stats/submit")
    config.add_view(stats_submit, route_name="stats_submit",
        renderer="index.jinja2")

    # SEARCH ROUTES
    config.add_route("search", "search")
    config.add_view(search, route_name="search",
        renderer="search.mako")

    config.add_route("search_paged", "search/page/{page:\d+}")
    config.add_view(search, route_name="search_paged",
        renderer="search.mako")


    return config.make_wsgi_app()
