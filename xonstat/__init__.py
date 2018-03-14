import sqlahelper
from pyramid_beaker import set_cache_regions_from_settings
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import JSONP
from sqlalchemy import engine_from_config
from xonstat.models import initialize_db
from xonstat.views import *
from xonstat.security import *


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # setup the database engine
    engine = engine_from_config(settings, 'sqlalchemy.', pool_size=5)
    sqlahelper.add_engine(engine)

    # initialize database structures
    initialize_db(engine)

    # set up beaker cache
    set_cache_regions_from_settings(settings)

    config = Configurator(settings=settings, root_factory=ACLFactory)

    # mako for templating
    config.include('pyramid_mako')

    # for json-encoded responses
    config.add_renderer('jsonp', JSONP(param_name='callback'))

    # for static assets
    config.add_static_view('static', 'xonstat:static')

    # robots
    config.add_route("robots", "robots.txt")
    config.add_view(robots, route_name="robots")

    # for 404s
    config.add_view(notfound, context=HTTPNotFound, renderer="404.mako")

    # ROOT ROUTE
    config.add_route("main_index", "/")
    config.add_view(main_index, route_name="main_index", renderer="main_index.mako")

    config.add_route("summary_stats_json", "/summary")
    config.add_view(view=summary_stats_json, route_name="summary_stats_json", renderer="json",
                    accept="application/json")

    # MAIN SUBMISSION ROUTE
    config.add_route("submit_stats", "stats/submit")
    config.add_view(submit_stats, route_name="submit_stats", renderer="submit_stats.mako")

    # PLAYER ROUTES
    config.add_route("player_game_index",      "/player/{player_id:\d+}/games")
    config.add_view(player_game_index,      route_name="player_game_index",      renderer="player_game_index.mako")

    config.add_route("player_game_index_json", "/player/{player_id:\d+}/games.json")
    config.add_view(player_game_index_json, route_name="player_game_index_json", renderer="jsonp")

    config.add_route("player_info",      "/player/{id:\d+}")
    config.add_view(player_info,      route_name="player_info",      renderer="player_info.mako")

    config.add_route("player_info_json", "/player/{id:\d+}.json")
    config.add_view(player_info_json, route_name="player_info_json", renderer="jsonp")

    config.add_route("player_hashkey_info_text", "/player/me")
    config.add_view(player_hashkey_info_text, route_name="player_hashkey_info_text", renderer="player_hashkey_info_text.mako")

    config.add_route("player_hashkey_info_json", "/player/me.json")
    config.add_view(player_hashkey_info_json, route_name="player_hashkey_info_json", renderer="jsonp")

    config.add_route("player_elo_info_text", "/player/{hashkey}/elo.txt")
    config.add_view(player_elo_info_text, route_name="player_elo_info_text", renderer="player_elo_info_text.mako")

    # FIXME - needs an additional method to convert to JSON
    config.add_route("player_elo_info_json", "/player/{hashkey}/elo.json")
    config.add_view(player_elo_info_json, route_name="player_elo_info_json", renderer="jsonp")

    config.add_route("player_accuracy",      "/player/{id:\d+}/accuracy")
    config.add_view(player_accuracy_json, route_name="player_accuracy",      renderer="jsonp")

    config.add_route("player_index",      "/players")
    config.add_view(player_index,      route_name="player_index",      renderer="player_index.mako")

    config.add_route("player_index_json", "/players.json")
    config.add_view(player_index_json, route_name="player_index_json", renderer="jsonp")

    config.add_route("player_captimes",      "/player/{player_id:\d+}/captimes")
    config.add_view(player_captimes,      route_name="player_captimes",      renderer="player_captimes.mako")

    config.add_route("player_captimes_json", "/player/{player_id:\d+}/captimes.json")
    config.add_view(player_captimes_json, route_name="player_captimes_json", renderer="jsonp")

    config.add_route("player_weaponstats_data_json", "/player/{id:\d+}/weaponstats.json")
    config.add_view(player_weaponstats_data_json, route_name="player_weaponstats_data_json", renderer="jsonp")

    config.add_route("top_players_index", "/topactive")
    config.add_view(top_players_index, route_name="top_players_index", renderer="top_players_index.mako")

    config.add_route("top_servers_index", "/topservers")
    config.add_view(top_servers_index, route_name="top_servers_index", renderer="top_servers_index.mako")

    config.add_route("top_maps_index", "/topmaps")
    config.add_view(top_maps_index, route_name="top_maps_index", renderer="top_maps_index.mako")

    config.add_route("player_versus", "/versus")
    config.add_view(player_versus, route_name="player_versus", renderer="player_versus.mako")

    # GAME ROUTES
    config.add_route("game_info",      "/game/{id:\d+}")
    config.add_view(game_info,      route_name="game_info",      renderer="game_info.mako")

    config.add_route("game_info_json", "/game/{id:\d+}.json")
    config.add_view(game_info_json, route_name="game_info_json", renderer="jsonp")

    config.add_route("game_index", "/games")
    config.add_view(game_finder, route_name="game_index", renderer="game_finder.mako")

    config.add_route("game_index_json", "/games.json")
    config.add_view(game_finder_json, route_name="game_index_json", renderer="jsonp")

    # SERVER ROUTES
    config.add_route("server_index", "/servers")
    config.add_view(view=ServerIndex, route_name="server_index", attr="html",
                    renderer="server_index.mako", accept="text/html")
    config.add_view(view=ServerIndex, route_name="server_index", attr="json", renderer="json",
                    accept="application/json")

    config.add_route("server_top_maps", "/server/{id:\d+}/topmaps")
    config.add_view(view=ServerTopMaps, route_name="server_top_maps", attr="html",
                    renderer="server_top_maps.mako", accept="text/html")
    config.add_view(view=ServerTopMaps, route_name="server_top_maps", attr="json", renderer="json",
                    accept="application/json")

    config.add_route("server_top_active", "/server/{id:\d+}/topactive")
    config.add_view(view=ServerTopPlayers, route_name="server_top_active", attr="html",
                    renderer="server_top_active.mako", accept="text/html")
    config.add_view(view=ServerTopPlayers, route_name="server_top_active", attr="json",
                    renderer="json", accept="application/json")

    config.add_route("server_top_scorers", "/server/{id:\d+}/topscorers")
    config.add_view(view=ServerTopScorers, route_name="server_top_scorers", attr="html",
                    renderer="server_top_scorers.mako", accept="text/html")
    config.add_view(view=ServerTopScorers, route_name="server_top_scorers", attr="json",
                    renderer="json", accept="application/json")

    config.add_route("server_info", "/server/{id:\d+}")
    config.add_view(view=ServerInfo, route_name="server_info", attr="html",
                    renderer="server_info.mako", accept="text/html")
    config.add_view(view=ServerInfo, route_name="server_info", attr="json", renderer="json",
                    accept="application/json")

    # MAP ROUTES
    config.add_route("map_index", "/maps")
    config.add_view(view=MapIndex, route_name="map_index", attr="html",
                    renderer="map_index.mako", accept="text/html")
    config.add_view(view=MapIndex, route_name="map_index", attr="json", renderer="json",
                    accept="application/json")

    config.add_route("map_top_scorers", "/map/{id:\d+}/topscorers")
    config.add_view(view=MapTopScorers, route_name="map_top_scorers", attr="html",
                    renderer="map_top_scorers.mako", accept="text/html")
    config.add_view(view=MapTopScorers, route_name="map_top_scorers", attr="json",
                    renderer="json", accept="application/json")

    config.add_route("map_top_active", "/map/{id:\d+}/topactive")
    config.add_view(view=MapTopPlayers, route_name="map_top_active", attr="html",
                    renderer="map_top_active.mako", accept="text/html")
    config.add_view(view=MapTopPlayers, route_name="map_top_active", attr="json",
                    renderer="json", accept="application/json")

    config.add_route("map_top_servers", "/map/{id:\d+}/topservers")
    config.add_view(view=MapTopServers, route_name="map_top_servers", attr="html",
                    renderer="map_top_servers.mako", accept="text/html")
    config.add_view(view=MapTopServers, route_name="map_top_servers", attr="json",
                    renderer="json", accept="application/json")

    config.add_route("map_info",      "/map/{id:\d+}")
    config.add_view(map_info,      route_name="map_info",      renderer="map_info.mako")

    config.add_route("map_info_json", "/map/{id:\d+}.json")
    config.add_view(map_info_json, route_name="map_info_json", renderer="jsonp")

    config.add_route("map_captimes",      "/map/{id:\d+}/captimes")
    config.add_view(map_captimes,      route_name="map_captimes",      renderer="map_captimes.mako")

    config.add_route("map_captimes_json", "/map/{id:\d+}/captimes.json")
    config.add_view(map_captimes_json, route_name="map_captimes_json", renderer="jsonp")

    # SEARCH ROUTES
    config.add_route("search",      "search")
    config.add_view(search,      route_name="search",      renderer="search.mako")

    config.add_route("search_json", "search.json")
    config.add_view(search_json, route_name="search_json", renderer="jsonp")

    # ADMIN ROUTES
    config.add_forbidden_view(forbidden, renderer="forbidden.mako")

    config.add_route("login", "/login")
    config.add_view(login, route_name="login", check_csrf=True, renderer="json")

    config.add_route("merge", "/admin/merge")
    config.add_view(merge, route_name="merge", renderer="merge.mako", permission="merge")

    return config.make_wsgi_app()
