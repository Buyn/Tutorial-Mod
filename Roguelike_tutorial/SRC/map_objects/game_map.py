# imports  {{{
import tcod as libtcod
from random import randint
from components.ai import BasicMonster
from components.fighter import Fighter
from game_messages import Message
from entity import Entity
from render_functions import RenderOrder
from map_objects.rectangle import Rect
from map_objects.tile import Tile
from components.item import Item
from item_functions import cast_confuse, heal, cast_lightning, cast_fireball
from components.stairs import Stairs
#  }}}

class GameMap:
    def __init__(self, width, height, dungeon_level=1): # Folding {{{
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level
        #  }}}
        
    def initialize_tiles(self): # Folding {{{
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]
        return tiles
        #  }}}


    def create_room(self, room): # Folding {{{
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False
                #  }}}
                

    def create_over_room(self, room): # Folding {{{
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 , room.x2 - 1):
            for y in range(room.y1, room.y2 - 1):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False
                #  }}}
                

    def make_test_map(self): # Folding {{{
        # Create two rooms for demonstration purposes
        room1 = Rect(20, 15, 10, 15)
        room2 = Rect(35, 15, 10, 15)
        self.create_room(room1)
        self.create_room(room2)
        self.create_h_tunnel(25, 40, 23)
        #  }}}
        

    def make_map(self,
                 max_rooms, room_min_size, room_max_size,
                 map_width, map_height,
                 player, entities,
                 max_monsters_per_room, max_items_per_room): # Folding {{{
        rooms = []
        num_rooms = 0
        center_of_last_room_x = None
        center_of_last_room_y = None
        for r in range(max_rooms):#   {{{
            # generate room coordinates  {{{
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)
            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)
            #  }}}
            # run through the other rooms and see if they intersect with this one#   {{{
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            #  }}}
            else:
                # this means there are no intersections, so this room is valid
                # "paint" it to the map's tiles
                self.create_room(new_room)
                # center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()
                center_of_last_room_x = new_x
                center_of_last_room_y = new_y
                if num_rooms == 0:# add player  {{{
                    # this is the first room, where the player starts t
                    player.x = new_x
                    player.y = new_y
                    #  }}}
                else: # connect with tunnels  {{{
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel
                    # center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()
                    # flip a coin (random number that is either 0 or 1)
                    if randint(0, 1) == 1:
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)
                    #  }}}
                    self.place_entities(new_room, entities, max_monsters_per_room, max_items_per_room)
                # finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1
        #  }}} end of make rooms loop
        # add stairs  {{{
        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', libtcod.white, 'Stairs',
                             render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)
            #  }}}
    #  }}}
                

    def create_h_tunnel(self, x1, x2, y): # Folding {{{
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
            #  }}}
            
    def create_v_tunnel(self, y1, y2, x): # Folding {{{
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
            #  }}}
            

    def place_entities(self, room, entities, max_monsters_per_room, max_items_per_room): # Folding {{{
        # Get a random number of monsters
        # Add items  {{{
        number_of_items = randint(0, max_items_per_room)
        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_chance = randint(0, 100)
                if item_chance < 70: # add Healing Potion  {{{
                    item_component = Item(use_function=heal, amount=4)
                    item = Entity(x, y, '!', libtcod.violet, 'Healing Potion', render_order=RenderOrder.ITEM,
                                  item=item_component)
                #  }}}
                elif item_chance < 80:#  add Fireball scroll {{{
                    item_component = Item(use_function=cast_fireball, targeting=True, targeting_message=Message(
                        'Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan),
                                          damage=12, radius=3)
                    item = Entity(x, y, '#', libtcod.red, 'Fireball Scroll', render_order=RenderOrder.ITEM,
                                  item=item_component)
                    #  }}}
                elif item_chance < 90:# Confusion Scroll  {{{
                    item_component = Item(use_function=cast_confuse,
                        targeting=True,
                        targeting_message=Message(
                            'Left-click an enemy to confuse it, or right-click to cancel.',
                            libtcod.light_cyan))
                    item = Entity(x, y, '#',
                                  libtcod.light_pink,
                                  'Confusion Scroll',
                                  render_order=RenderOrder.ITEM,
                                  item=item_component)
                    #  }}}
                else: # add  Lightning Scroll {{{
                    item_component = Item(use_function=cast_lightning, damage=20, maximum_range=5)
                    item = Entity(x, y, '#', libtcod.yellow, 'Lightning Scroll', render_order=RenderOrder.ITEM,
                                  item=item_component)
                entities.append(item)
                #  }}}
                #  }}}
        # add Monsters  {{{
        number_of_monsters = randint(0, max_monsters_per_room)
        for i in range(number_of_monsters):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                if randint(0, 100) < 80:
                    # make Orc  {{{
                    fighter_component = Fighter(hp=10, defense=0, power=3)
                    ai_component = BasicMonster()
                    monster = Entity(
                        x, y,
                        'o', libtcod.desaturated_green, 'Orc',
                        blocks=True, render_order=RenderOrder.ACTOR,  
                        fighter=fighter_component, ai=ai_component)
                    #  }}}
                else:
                    # Make Trole  {{{
                    fighter_component = Fighter(hp=16, defense=1, power=4)
                    ai_component = BasicMonster()
                    monster = Entity(
                        x, y,
                        'T', libtcod.darker_green, 'Troll',
                        blocks=True, render_order=RenderOrder.ACTOR, 
                        fighter=fighter_component, ai=ai_component)
                    #  }}}
                entities.append(monster)
            #  }}}
            #  }}}
                
    def is_blocked(self, x, y): # Folding {{{
        if self.tiles[x][y].blocked:
            return True
        return False
        #  }}}


    def next_floor(self, player, message_log, constants): #   {{{
        self.dungeon_level += 1
        entities = [player]
        self.tiles = self.initialize_tiles()
        self.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                      constants['map_width'], constants['map_height'], player, entities,
                      constants['max_monsters_per_room'], constants['max_items_per_room'])
        player.fighter.heal(player.fighter.max_hp // 2)
        message_log.add_message(Message('You take a moment to rest, and recover your strength.', libtcod.light_violet))
        return entities
    #  }}}
    
