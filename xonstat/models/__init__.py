"""
Model initialization and mapping.
"""

from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, mapper

from xonstat.models.game import *
from xonstat.models.main import *
from xonstat.models.map import *
from xonstat.models.player import *
from xonstat.models.server import *

DBSession = scoped_session(sessionmaker())
Base = declarative_base()


def initialize_db(engine=None):
    """
    Initialize the database using reflection.

    :param engine: The SQLAlchemy engine instance to bind.
    :return: None
    """
    DBSession.configure(bind=engine)

    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

    # Since the schema is actually defined elsewhere, we use reflection to determine the
    # structure of the models instead of specifying them over again in Python.
    metadata = MetaData(bind=engine)
    metadata.reflect()

    # Assign all the tables to objects
    achievements_table = metadata.tables['achievements']
    cd_achievement_table = metadata.tables['cd_achievement']
    cd_game_type_table = metadata.tables['cd_game_type']
    cd_weapon_table = metadata.tables['cd_weapon']
    db_version_table = metadata.tables['db_version']
    games_table = metadata.tables['games']
    hashkeys_table = metadata.tables['hashkeys']
    maps_table = metadata.tables['maps']
    player_game_stats_table = metadata.tables['player_game_stats']
    players_table = metadata.tables['players']
    player_weapon_stats_table = metadata.tables['player_weapon_stats']
    servers_table = metadata.tables['servers']
    player_nicks_table = metadata.tables['player_nicks']
    player_elos_table = metadata.tables['player_elos']
    player_ranks_table = metadata.tables['player_ranks']
    player_captimes_table = metadata.tables['player_map_captimes']
    summary_stats_table = metadata.tables['summary_stats']
    team_game_stats_table = metadata.tables['team_game_stats']
    player_game_anticheats_table = metadata.tables['player_game_anticheats']
    player_groups_table = metadata.tables['player_groups']
    active_players_table = metadata.tables['active_players_mv']
    active_servers_table = metadata.tables['active_servers_mv']
    active_maps_table = metadata.tables['active_maps_mv']
    player_medals_table = metadata.tables['player_medals']
    player_game_frag_matrix_table = metadata.tables['player_game_frag_matrix']

    # Map the tables and the objects together
    mapper(PlayerAchievement, achievements_table)
    mapper(Achievement, cd_achievement_table)
    mapper(GameType, cd_game_type_table)
    mapper(Weapon, cd_weapon_table)
    mapper(Game, games_table)
    mapper(Hashkey, hashkeys_table)
    mapper(Map, maps_table)
    mapper(PlayerGameStat, player_game_stats_table)
    mapper(Player, players_table)
    mapper(PlayerWeaponStat, player_weapon_stats_table)
    mapper(Server, servers_table)
    mapper(PlayerNick, player_nicks_table)
    mapper(PlayerElo, player_elos_table)
    mapper(PlayerRank, player_ranks_table)
    mapper(PlayerCaptime, player_captimes_table)
    mapper(SummaryStat, summary_stats_table)
    mapper(TeamGameStat, team_game_stats_table)
    mapper(PlayerGameAnticheat, player_game_anticheats_table)
    mapper(PlayerGroups, player_groups_table)
    mapper(ActivePlayer, active_players_table)
    mapper(ActiveServer, active_servers_table)
    mapper(ActiveMap, active_maps_table)
    mapper(PlayerMedal, player_medals_table)
    mapper(PlayerGameFragMatrix, player_game_frag_matrix_table)
