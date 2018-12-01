#!/usr/bin/python2

#-------------------------------------------------------------------------------
#    Filename: toads_adventure.py
#
#      Author: David C. Drake (https://davidcdrake.com)
#
# Description: Contains a 'ToadsAdventure' class for managing a platformer game
#              developed using Python 2.7 and PyGame 1.9.
#-------------------------------------------------------------------------------

import sys
from pygame import mouse, mixer
import game
import tileset
import map
import characters
from config import *

#-------------------------------------------------------------------------------
#       Class: ToadsAdventure
#
# Description: Manages the "Toad's Adventure" platformer game.
#
#     Methods: __init__, load_level, game_logic, paint
#-------------------------------------------------------------------------------
class ToadsAdventure(game.Game):
    #---------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Initializes "Toad's Adventure" and loads a given level.
    #
    #      Inputs: level                    - Number indicating desired level.
    #              map_tiles_filename       - Name of map tileset file.
    #              character_tiles_filename - Name of character tileset file.
    #              fps                      - Desired frames per second
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def __init__(self, level, map_tiles_filename, character_tiles_filename,
                 fps=FRAMES_PER_SECOND):
        game.Game.__init__(self, fps)
        self.map_tiles = tileset.Tileset(map_tiles_filename, MAP_TILE_SIZE)
        self.character_tiles = tileset.Tileset(character_tiles_filename,
                                               CHARACTER_TILE_SIZE)
        if level < 1 or level > NUM_LEVELS:
            level = 1
        self.current_level = level
        mixer.init()
        self.load_level(self.current_level)
        mouse.set_visible(False)

    #---------------------------------------------------------------------------
    #      Method: load_level
    #
    # Description: Initializes map, characters, and music for a given level.
    #
    #      Inputs: level - Number corresponding to the desired level.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def load_level(self, level):
        self.map = map.Map(level, self.map_tiles, self.screen, self.width,
                           self.height)
##        self.items = []
##        for item in ITEM_LOCATIONS[level]:
##            self.items.append(Item(item[0], # ID number self.character_tiles,
##                                   self.map, self.screen,
##                                   (item[1] - 1) * MAP_TILE_SIZE,
##                                   (item[2] - 1) * MAP_TILE_SIZE))
        self.NPCs = []
        for NPC in NPC_LOCATIONS[level]:
            self.NPCs.append(characters.NonPlayerCharacter(
                NPC[0], self.character_tiles, self.map, self.screen,
                (NPC[1] - 1) * MAP_TILE_SIZE, (NPC[2] - 1) * MAP_TILE_SIZE))
        self.player = characters.PlayerCharacter(
            self.character_tiles, self.map, self.screen,
            (PLAYER_START_LOCATION[level][0] - 1) * MAP_TILE_SIZE,
            (PLAYER_START_LOCATION[level][1] - 1) * MAP_TILE_SIZE)
        mixer.music.load(MUSIC[level])
        mixer.music.play(-1) # -1 for infinite looping

    #---------------------------------------------------------------------------
    #      Method: game_logic
    #
    # Description: Determines game behavior according to keyboard input and
    #              interactions among all active objects.
    #
    #      Inputs: keys     - Keys that are currently pressed down.
    #              new_keys - Keys that have just begun to be pressed down.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def game_logic(self, keys, new_keys):
        if self.player.get_tile_number_behind() == OPEN_DOOR: # level complete
            mixer.music.fadeout(MUSIC_FADEOUT_LENGTH)
            self.player.victory_pose()
            self.current_level += 1
            if self.current_level > NUM_LEVELS:
                self.current_level = 1
            self.load_level(self.current_level)
        else: # level incomplete, so execute each character's game logic
            self.player.game_logic(keys, new_keys)
            for NPC in self.NPCs:
                if NPC.overlaps(self.player):
                    self.player.take_damage()
                if NPC.y > self.map.map_height * MAP_TILE_SIZE:
                    self.NPCs.remove(NPC)
                else:
                    NPC.game_logic()

    #---------------------------------------------------------------------------
    #      Method: paint
    #
    # Description: Draws the map/level and active game objects onto the screen.
    #
    #      Inputs: surface - The surface onto which everything will be drawn.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def paint(self, surface):
        # determine top-left pixel to be displayed
        x = self.player.x - (self.width / 2)
        y = self.player.y - (self.height / 2)

        # draw currently-visible map tiles and game characters
        self.map.draw(x, y)
        self.player.draw((self.width / 2 - MAP_TILE_SIZE,
                          self.height / 2 - MAP_TILE_SIZE))
        for NPC in self.NPCs:
            NPC.draw(x, y)

#-------------------------------------------------------------------------------
#    Function: main
#
# Description: Creates and runs "Toad's Adventure." If a command-line integer is
#              provided, it may determine the starting level, otherwise the game
#              starts at level 1.
#
#      Inputs: None, but starting level may be set via command line.
#
#     Outputs: None.
#-------------------------------------------------------------------------------
def main():
    if len(sys.argv) > 1:
        starting_level = int(sys.argv[1])
    else:
        starting_level = 1
    game = ToadsAdventure(starting_level, MAP_TILES_FILENAME,
                          CHARACTER_TILES_FILENAME)
    game.main_loop()

if __name__ == '__main__':
    main()
