# import  {{{
import os
import shelve
from pip._vendor.html5lib.constants import entities
#  }}}


def save_game(player, entities, game_map, message_log, game_state):#   {{{
    with shelve.open('save\\savegame.db') as data_file:
        data_file['player_index'] = entities.index(player)
        data_file['entities'] = entities
        data_file['game_map'] = game_map
        data_file['message_log'] = message_log
        data_file['game_state'] = game_state
    #  }}}

def load_game():#   {{{
    if not os.path.isfile('save\\savegame.db.dat'):
        raise FileNotFoundError

    print("start file load")
    with shelve.open('save\\savegame.db') as data_file:
        print("file open")
        player_index = data_file['player_index']
        print("player read")
        entities = data_file['entities']
        game_map = data_file['game_map']
        message_log = data_file['message_log']
        game_state = data_file['game_state']
        print("file endet")

    player = entities[player_index]

    return player, entities, game_map, message_log, game_state
    #  }}}


def save_char(player, entities):#   {{{
    with shelve.open('save\\char.db') as data_file:
        data_file['player_index'] = entities.index(player)
        data_file['entities'] = entities
    #  }}}


def load_char():#   {{{
    if not os.path.isfile('save\\char.db.dat'):
        return None
    with shelve.open('save\\char.db') as data_file:
        player_index = data_file['player_index']
        entities = data_file['entities']
    player = entities[player_index]
    return player
    #  }}}


def import_char(player, entities):#   {{{
    if not os.path.isfile('save\\char.db.dat'):
        return player, entities
    with shelve.open('save\\char.db') as data_file:
        new_player_index = data_file['player_index']
        new_entities = data_file['entities']
    new_player = new_entities[new_player_index]
    player_index = entities.index(player)
    new_player.x = player.x
    new_player.y = player.y
    entities[player_index] = new_player
    player = new_player
    return player, entities
    #  }}}


def save_citadel(player, entities, game_map, message_log, game_state):#   {{{
    with shelve.open('save\\citadel.db') as data_file:
        data_file['player_index'] = entities.index(player)
        data_file['entities'] = entities
        data_file['game_map'] = game_map
        data_file['message_log'] = message_log
        data_file['game_state'] = game_state
    #  }}}


def load_citadel():#   {{{
    if not os.path.isfile('save\\citadel.db.dat'):
        raise FileNotFoundError
    with shelve.open('save\\citadel.db') as data_file:
        player_index = data_file['player_index']
        entities = data_file['entities']
        game_map = data_file['game_map']
        message_log = data_file['message_log']
        game_state = data_file['game_state']
    player = entities[player_index]
    return player, entities, game_map, message_log, game_state
    #  }}}
