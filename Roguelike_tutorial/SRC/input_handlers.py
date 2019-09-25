import tcod as libtcod
from game_states import GameStates


def handle_keys(key, game_state): #   {{{
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state in (
            GameStates.SHOW_INVENTORY,
            GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)
    return {}
    #  }}}


def handle_player_turn_keys(key): #   {{{
    key_char = chr(key.c)
    # Action Keys  {{{
    if key_char == 'g':
        return {'pickup': True}
    elif key_char == 'i':
        return {'show_inventory': True}
    elif key_char == 'd':
        return {'drop_inventory': True}
    elif key.vk == libtcod.KEY_ENTER:
        return {'take_stairs': True}
    #  }}}
    # Movement keys   {{{
    if key.vk == libtcod.KEY_UP or key_char == 'k':
        return {'move': (0, -1)}
    elif key.vk == libtcod.KEY_DOWN or key_char == 'j':
        return {'move': (0, 1)}
    elif key.vk == libtcod.KEY_LEFT or key_char == 'h':
        return {'move': (-1, 0)}
    elif key.vk == libtcod.KEY_RIGHT or key_char == 'l':
        return {'move': (1, 0)}
    elif key_char == 'y':
        return {'move': (-1, -1)}
    elif key_char == 'u':
        return {'move': (1, -1)}
    elif key_char == 'b':
        return {'move': (-1, 1)}
    elif key_char == 'n':
        return {'move': (1, 1)}
        #  }}}
    # Alt+Enter: toggle full screen {{{
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        return {'fullscreen': True}
        #  }}}
    # Exit the game {{{
    elif key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}
    #  }}}
    # No key was pressed
    return {}
    #  }}}


def handle_inventory_keys(key): #   {{{
    index = key.c - ord('a')
    if index >= 0:
        return {'inventory_index': index}
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the menu
        return {'exit': True}
    return {}
    #  }}}


def handle_player_dead_keys(key): #   {{{
    key_char = chr(key.c)
    if key_char == 'i':
        return {'show_inventory': True}
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the menu
        return {'exit': True}
    return {}
    #  }}}


def handle_targeting_keys(key):#   {{{
    if key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}
    return {}
    #  }}}


def handle_mouse(mouse):#   {{{
    if mouse.lbutton_pressed:
        (x, y) = (mouse.cx, mouse.cy)
        return {'left_click': (x, y)}
    elif mouse.rbutton_pressed:
        (x, y) = (mouse.cx, mouse.cy)
        return {'right_click': (x, y)}
    return {}
    #  }}}


def handle_main_menu(key):#   {{{
    key_char = chr(key.c)
    if key_char == 'a':
        return {'new_game': True}
    elif key_char == 'b':
        return {'load_game': True}
    elif key_char == 'c' :
        return {'citadel': True}
    elif key_char == 'd' or  key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}
    return {}
    #  }}}

# Todos  {{{
#todo передовать наружу колбек фунуцию с параметрами запуска в виде полььского стека вначале пораметры
#todo Заменить кнопки на события и потом отдельная вункчия преобразует стрингу дествия в параметры+колбек

#  }}}
