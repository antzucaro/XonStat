import sqlahelper
from pyramid.config import Configurator
from pyramid.renderers import JSONP
from sqlalchemy import engine_from_config
from xonstat.models import initialize_db
from xonstat.views import *

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # setup the database engine
    engine = engine_from_config(settings, 'sqlalchemy.', pool_size=5)
    sqlahelper.add_engine(engine)

    # initialize database structures
    initialize_db(engine)

    config = Configurator(settings=settings)

    config.add_static_view('static', 'xonstat:static')

    config.add_renderer('jsonp', JSONP(param_name='callback'))

    # ROOT ROUTE
    config.add_route("main_index", "/")
    config.add_view(main_index, route_name="main_index", renderer="main_index.mako")

    # MAIN SUBMISSION ROUTE
    config.add_route("stats_submit", "stats/submit")
    config.add_view(stats_submit, route_name="stats_submit")

    # PLAYER ROUTES
    config.add_route("player_game_index",      "/player/{player_id:\d+}/games")
    config.add_route("player_game_index_json", "/player/{player_id:\d+}/games.json")
    config.add_view(player_game_index,      route_name="player_game_index",      renderer="player_game_index.mako")
    config.add_view(player_game_index_json, route_name="player_game_index_json", renderer="jsonp")

    config.add_route("player_info",      "/player/{id:\d+}")
    config.add_route("player_info_json", "/player/{id:\d+}.json")
    config.add_view(player_info,      route_name="player_info",      renderer="player_info.mako")
    config.add_view(player_info_json, route_name="player_info_json", renderer="jsonp")

    config.add_route("player_hashkey_info_json", "/hashkey/{hashkey}")
    config.add_view(player_hashkey_info_json, route_name="player_hashkey_info_json", renderer="jsonp")

    config.add_route("player_elo_info_json", "/elo/{hashkey}")
    config.add_view(player_elo_info_json, route_name="player_elo_info_json", renderer="jsonp")

    config.add_route("player_accuracy",      "/player/{id:\d+}/accuracy")
    config.add_route("player_accuracy_json", "/player/{id:\d+}/accuracy.json")
    config.add_view(player_accuracy_json, route_name="player_accuracy",      renderer="jsonp")
    config.add_view(player_accuracy_json, route_name="player_accuracy_json", renderer="jsonp")

    config.add_route("player_index",      "/players")
    config.add_route("player_index_json", "/players.json")
    config.add_view(player_index,      route_name="player_index",      renderer="player_index.mako")
    config.add_view(player_index_json, route_name="player_index_json", renderer="jsonp")

    config.add_route("player_damage", "/player/{id:\d+}/damage")
    config.add_view(player_damage_json, route_name="player_damage",
        renderer="json")

    # GAME ROUTES
    config.add_route("game_index",      "/games")
    config.add_route("game_index_json", "/games.json")
    config.add_view(game_index,      route_name="game_index",      renderer="game_index.mako")
    config.add_view(game_index_json, route_name="game_index_json", renderer="jsonp")

    config.add_route("game_info",      "/game/{id:\d+}")
    config.add_route("game_info_json", "/game/{id:\d+}.json")
    config.add_view(game_info,      route_name="game_info",      renderer="game_info.mako")
    config.add_view(game_info_json, route_name="game_info_json", renderer="jsonp")

    config.add_route("rank_index",      "/ranks/{game_type_cd:ctf|dm|tdm|duel}")
    config.add_route("rank_index_json", "/ranks/{game_type_cd:ctf|dm|tdm|duel}.json")
    config.add_view(rank_index,      route_name="rank_index",      renderer="rank_index.mako")
    config.add_view(rank_index_json, route_name="rank_index_json", renderer="jsonp")

    # SERVER ROUTES
    config.add_route("server_index",      "/servers")
    config.add_route("server_index_json", "/servers.json")
    config.add_view(server_index,      route_name="server_index",      renderer="server_index.mako")
    config.add_view(server_index_json, route_name="server_index_json", renderer="jsonp")

    config.add_route("server_game_index",      "/server/{server_id:\d+}/games/page/{page:\d+}")
    config.add_route("server_game_index_json", "/server/{server_id:\d+}/games.json")
    config.add_view(server_game_index,      route_name="server_game_index",      renderer="server_game_index.mako")
    config.add_view(server_game_index_json, route_name="server_game_index_json", renderer="jsonp")

    config.add_route("server_info",      "/server/{id:\d+}")
    config.add_route("server_info_json", "/server/{id:\d+}.json")
    config.add_view(server_info,      route_name="server_info",      renderer="server_info.mako")
    config.add_view(server_info_json, route_name="server_info_json", renderer="jsonp")

    # MAP ROUTES
    config.add_route("map_index",      "/maps")
    config.add_route("map_index_json", "/maps.json")
    config.add_view(map_index,      route_name="map_index",      renderer="map_index.mako")
    config.add_view(map_index_json, route_name="map_index_json", renderer="jsonp")

    config.add_route("map_info",      "/map/{id:\d+}")
    config.add_route("map_info_json", "/map/{id:\d+}.json")
    config.add_view(map_info,      route_name="map_info",      renderer="map_info.mako")
    config.add_view(map_info_json, route_name="map_info_json", renderer="jsonp")

    # SEARCH ROUTES
    config.add_route("search",      "search")
    config.add_route("search_json", "search.json")
    config.add_view(search,      route_name="search",      renderer="search.mako")
    config.add_view(search_json, route_name="search_json", renderer="jsonp")

    return config.make_wsgi_app()
