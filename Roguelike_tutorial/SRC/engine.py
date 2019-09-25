# imports  {{{
import libtcodpy as libtcod

from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from loader_functions.data_loaders import load_game, save_game, save_char, load_char, save_citadel, load_citadel, import_char
from menus import main_menu, message_box
from loader_functions.initialize_new_game import get_constants, get_game_variables
from render_functions import clear_all, render_all
#  }}}


def main():#   {{{
    # init menu setings  {{{
    constants = get_constants()
    # Console {{{
    libtcod.console_set_custom_font('arial10x10.png',
        libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(constants['screen_width'],
                              constants['screen_height'],
                              constants['window_title'], False)
    con = libtcod.console_new(constants['screen_width'],
                              constants['screen_height'])
    panel = libtcod.console_new(constants['screen_width'],
                                constants['panel_height'])
    #  }}}
    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None
    show_main_menu = True
    show_load_error_message = False
    main_menu_background_image = libtcod.image_load('menu_background1.png')
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    #  }}}
    while not libtcod.console_is_window_closed():#   {{{
        libtcod.sys_check_for_event(
            libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE,
            key, mouse)
        if show_main_menu:#   {{{
            main_menu(con, main_menu_background_image,
                      constants['screen_width'],
                      constants['screen_height'])
            if show_load_error_message:#   {{{
                    message_box(con, 'No save game to load', 50,
                                constants['screen_width'],
                                constants['screen_height'])
                #  }}}

            libtcod.console_flush()

            action = handle_main_menu(key)
            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')
            citadel = action.get('citadel')

            # show error  {{{
            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
                #  }}}
            elif new_game:#   {{{
                player, entities, game_map, message_log, game_state = get_game_variables(constants)
                player, entities = import_char( player, entities)
                game_state = GameStates.PLAYERS_TURN
                show_main_menu = False
                #  }}}
            elif load_saved_game:#   {{{
                try:
                    player, entities, game_map, message_log, game_state = load_game()
                    player, entities = import_char( player, entities)
                    show_main_menu = False
                    citadel = False
                except FileNotFoundError:
                    show_load_error_message = True
                #  }}}
            elif citadel:#   {{{
                try:
                    player, entities, game_map, message_log, game_state = load_citadel()
                    player, entities = import_char( player, entities)
                    show_main_menu = False
                except FileNotFoundError:
                    player, entities, game_map, message_log, game_state = get_game_variables(constants)
                    show_load_error_message = True
                    show_main_menu = False
                    game_state = GameStates.PLAYERS_TURN
                #  }}}
            elif exit_game:#   {{{
                break
                #  }}}
        # }}}end of main menu  
        else:# start game  {{{
            libtcod.console_clear(con)
            if citadel:
                play_citadel(player, entities, game_map, message_log,
                      game_state, con, panel, constants)
            else:
                play_game(player, entities, game_map, message_log,
                      game_state, con, panel, constants)
            citadel = False
            show_main_menu = True
        #  }}}
    # }}}end of main loop  
#  }}}
            

def play_game(player, entities, game_map, message_log, game_state, con, panel, constants):#   {{{
    # Main Loop Inits {{{
    # FOV {{{
    fov_map = initialize_fov(game_map)
    fov_recompute = True
    #  }}}
    game_state = GameStates.PLAYERS_TURN
    previous_game_state = game_state
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    targeting_item = None
    #  }}}
    # ============================== 
    # main loop {{{
    while not libtcod.console_is_window_closed():
        # Rendering {{{
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y,
                          constants['fov_radius'],
                          constants['fov_light_walls'],
                          constants['fov_algorithm'])
        render_all(con, panel, entities, player, game_map, fov_map,
                   fov_recompute, message_log,
                   constants['screen_width'],
                   constants['screen_height'],
                   constants['bar_width'],
                   constants['panel_height'], constants['panel_y'],
                   mouse, constants['colors'], game_state)
        fov_recompute = False
        libtcod.console_flush()
        clear_all(con, entities)
        #  }}}
        # events {{{
        libtcod.sys_check_for_event(
            libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE,
            key, mouse)
        # Actions Handlers  {{{
        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)
        
        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        move = action.get('move')
        inventory_index = action.get('inventory_index')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')
        pickup = action.get('pickup')
        take_stairs = action.get('take_stairs')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        player_turn_results = []
        dx = dy = 0
        #  }}}
        # Move Player {{{
        if move and game_state ==  GameStates.PLAYERS_TURN :
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy
            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)
                if target:
                        # player.kick(target, dx, dy,#   {{{
                        #         game_map.is_blocked(
                        #             destination_x + dx,
                        #             destination_y + dy))
                        #  }}}
                        attack_results = player.fighter.attack(target)
                        player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    fov_recompute = True
                game_state = GameStates.ENEMY_TURN
            #  }}}
        # Pickup  {{{
        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)
                    break
            else:
                message_log.add_message(Message('There is nothing here to pick up.', libtcod.yellow))
        #  }}}
        if show_inventory: #   {{{
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY
            #  }}}
        # inventory_index #   {{{
        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.SHOW_INVENTORY:
                # player_turn_results.extend(
                #     player.inventory.use(
                #         item, entities=entities,
                #         fov_map=fov_map))
                    player_turn_results.extend( player.inventory.use( item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                 player_turn_results.extend(
                     player.inventory.drop_item(item))
            #  }}}
        if drop_inventory: #   {{{
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY
            #  }}}
        if game_state == GameStates.TARGETING:#   {{{
            if left_click:
                target_x, target_y = left_click
                item_use_results = player.inventory.use(
                    targeting_item, entities=entities,
                    fov_map=fov_map,
                    target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})
            #  }}}
        if take_stairs and game_state == GameStates.PLAYERS_TURN:#   {{{
            for entity in entities:
                if entity.stairs and entity.x == player.x and entity.y == player.y:
                    entities = game_map.next_floor(player, message_log, constants)
                    fov_map = initialize_fov(game_map)
                    fov_recompute = True
                    libtcod.console_clear(con)
                    break
            else:
                message_log.add_message(Message('There are no stairs here.', libtcod.yellow))
            #  }}}
        if exit: # Folding {{{
            if game_state == GameStates.SHOW_INVENTORY or GameStates.DROP_INVENTORY :
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({
                    'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map,
                          message_log, game_state)
                save_char(player, entities)
                return True
        #  }}}
        if fullscreen: # Folding {{{
            print("Tray FullScreen")
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        #  }}}
        # Player result rutin  {{{
        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get(
                                    'targeting_cancelled')
            xp = player_turn_result.get('xp')
            if message: #   {{{
                message_log.add_message(message)
                #  }}}
            if dead_entity: #   {{{
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    if dx or dy:
                        player.kick(dead_entity, dx, dy,
                                game_map.is_blocked(
                                    destination_x + dx,
                                    destination_y + dy))
                    message = kill_monster(dead_entity)
                message_log.add_message(message)
                #  }}}
            if item_added: #   {{{
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN
                #  }}}
            if item_consumed:#   {{{
                game_state = GameStates.ENEMY_TURN
                #  }}}
            if targeting:#   {{{
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING
                targeting_item = targeting
                message_log.add_message(
                    targeting_item.item.targeting_message)
                #  }}}
            if item_dropped:#   {{{
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURN
                #  }}}
            if targeting_cancelled:#   {{{
                game_state = previous_game_state
                message_log.add_message(Message(
                    'Targeting cancelled'))
                #  }}}
            if xp:#   {{{
                leveled_up = player.level.add_xp(xp)
                message_log.add_message(Message('You gain {0} experience points.'.format(xp)))

                if leveled_up:
                    message_log.add_message(Message(
                        'Your battle skills grow stronger! You reached level {0}'.format(
                            player.level.current_level) + '!', libtcod.yellow))
                    previous_game_state = game_state
                    game_state = GameStates.LEVEL_UP
                #  }}}
            #  }}}
        # Enaemy turn {{{
        if game_state == GameStates.ENEMY_TURN:
            # print("enemy turn")
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)
                    for enemy_turn_result in enemy_turn_results: #   {{{
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')
                        if message:
                            message_log.add_message(message)
                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)
                                message_log.add_message(message)
                        if game_state == GameStates.PLAYER_DEAD:
                                    break
                        #  end  enemy turn result rutine }}}
                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                game_state = GameStates.PLAYERS_TURN
            #  }}}
        # }}}  events
    # end of main loop  }}}
#  }}}


def play_citadel(player, entities, game_map, message_log, game_state, con, panel, constants):#   {{{
    # Main Loop Inits {{{
    # FOV {{{
    fov_map = initialize_fov(game_map)
    fov_recompute = True
    #  }}}
    game_state = GameStates.PLAYERS_TURN
    previous_game_state = game_state
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    targeting_item = None
    #  }}}
    # ============================== 
    # main loop {{{
    while not libtcod.console_is_window_closed():
        # Rendering {{{
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y,
                          constants['fov_radius'],
                          constants['fov_light_walls'],
                          constants['fov_algorithm'])
        render_all(con, panel, entities, player, game_map, fov_map,
                   fov_recompute, message_log,
                   constants['screen_width'],
                   constants['screen_height'],
                   constants['bar_width'],
                   constants['panel_height'], constants['panel_y'],
                   mouse, constants['colors'], game_state)
        fov_recompute = False
        libtcod.console_flush()
        clear_all(con, entities)
        #  }}}
        # events {{{
        libtcod.sys_check_for_event(
            libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE,
            key, mouse)
        # Actions Handlers  {{{
        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)
        
        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        move = action.get('move')
        inventory_index = action.get('inventory_index')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')

        player_turn_results = []
        dx = dy = 0
        #  }}}
        # Move Player {{{
        if move and game_state ==  GameStates.PLAYERS_TURN :
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy
            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)
                if target:
                        # player.kick(target, dx, dy,#   {{{
                        #         game_map.is_blocked(
                        #             destination_x + dx,
                        #             destination_y + dy))
                        #  }}}
                        attack_results = player.fighter.attack(target)
                        player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    fov_recompute = True
                game_state = GameStates.ENEMY_TURN
            #  }}}
        # Pickup  {{{
        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)
                    break
            else:
                message_log.add_message(Message('There is nothing here to pick up.', libtcod.yellow))
        #  }}}
        if show_inventory: #   {{{
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY
            #  }}}
        # inventory_index #   {{{
        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.SHOW_INVENTORY:
                # player_turn_results.extend(
                #     player.inventory.use(
                #         item, entities=entities,
                #         fov_map=fov_map))
                    player_turn_results.extend( player.inventory.use( item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                 player_turn_results.extend(
                     player.inventory.drop_item(item))
            #  }}}
        if drop_inventory: #   {{{
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY
            #  }}}
        if game_state == GameStates.TARGETING:#   {{{
            if left_click:
                target_x, target_y = left_click
                item_use_results = player.inventory.use(
                    targeting_item, entities=entities,
                    fov_map=fov_map,
                    target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})
            #  }}}
        if exit: # Folding {{{
            if game_state == GameStates.SHOW_INVENTORY or GameStates.DROP_INVENTORY :
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({
                    'targeting_cancelled': True})
            else:
                save_citadel(player, entities, game_map,
                          message_log, game_state)
                save_char(player, entities)
                return True
        #  }}}
        if fullscreen: # Folding {{{
            print("Tray FullScreen")
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        #  }}}
        # Player result rutin  {{{
        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get(
            'targeting_cancelled')
            if message: #   {{{
                message_log.add_message(message)
                #  }}}
            if dead_entity: #   {{{
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    if dx or dy:
                        player.kick(dead_entity, dx, dy,
                                game_map.is_blocked(
                                    destination_x + dx,
                                    destination_y + dy))
                    message = kill_monster(dead_entity)
                message_log.add_message(message)
                #  }}}
            if item_added: #   {{{
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN
                #  }}}
            if item_consumed:#   {{{
                game_state = GameStates.ENEMY_TURN
                #  }}}
            if targeting:#   {{{
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING
                targeting_item = targeting
                message_log.add_message(
                    targeting_item.item.targeting_message)
                #  }}}
            if item_dropped:#   {{{
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURN
                #  }}}
            if targeting_cancelled:#   {{{
                game_state = previous_game_state
                message_log.add_message(Message(
                    'Targeting cancelled'))
                #  }}}
            #  }}}
        # Enaemy turn {{{
        if game_state == GameStates.ENEMY_TURN:
            # print("enemy turn")
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)
                    for enemy_turn_result in enemy_turn_results: #   {{{
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')
                        if message:
                            message_log.add_message(message)
                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)
                                message_log.add_message(message)
                        if game_state == GameStates.PLAYER_DEAD:
                                    break
                        #  end  enemy turn result rutine }}}
                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                game_state = GameStates.PLAYERS_TURN
            #  }}}
        # }}}  events
    # end of main loop  }}}
#  }}}


if __name__ == '__main__':
    main()

# TODO: {{{
    # Todo Переместить сушности предметов плэера и мостров в расзные класы унаследововав каждый от сушности
    # TODO передовать константу упрастив вызов функций
    # и возможно продолжить долней шее наследование уже подкласов типов предметов типов монстров класов персонажа
#  }}}
