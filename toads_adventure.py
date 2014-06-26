#!/usr/bin/env python

#------------------------------------------------------------------------------
#    Filename: toads_adventure.py
#
#      Author: David C. Drake (www.davidcdrake.com)
#
# Description: Contains a 'ToadsAdventure' class for managing the "Toad's
#              Adventure" platformer game. Developed using Python 2.7.2 and
#              PyGame 1.9.2a0.
#------------------------------------------------------------------------------

import sys
import pygame
import game
import tileset
import map
from characters import *
from config import *

#------------------------------------------------------------------------------
#       Class: ToadsAdventure
#
# Description: Manages the "Toad's Adventure" platformer game.
#------------------------------------------------------------------------------
class ToadsAdventure(game.Game):
    #--------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Initializes the "Toad's Adventure" game and loads its first
    #              level.
    #
    #      Inputs: level                    - The starting level number.
    #              mapTilesetFilename       - Name of the map tileset file.
    #              characterTilesetFilename - Name of the game character
    #                                         tileset file.
    #              screenWidth              - Width of the game window.
    #              screenHeight             - Height of the game window.
    #              fps                      - Frames per second
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def __init__(self,
                 level,
                 mapTilesetFilename,
                 characterTilesetFilename,
                 screenWidth,
                 screenHeight,
                 fps):
        self.currentLevel             = level
        self.mapTilesetFilename       = mapTilesetFilename
        self.characterTilesetFilename = characterTilesetFilename
        self.screenWidth              = screenWidth
        self.screenHeight             = screenHeight
        game.Game.__init__(self,
                           NAME,
                           screenWidth * MAP_TILE_SIZE,
                           screenHeight * MAP_TILE_SIZE,
                           fps)

        # Initialize tilesets:
        self.mapTiles       = tileset.Tileset(self.mapTilesetFilename,
                                              MAP_TILE_SIZE)
        self.characterTiles = tileset.Tileset(self.characterTilesetFilename,
                                              CHARACTER_TILE_SIZE)

        # Initialize music mixer:
        pygame.mixer.init()

        # Load the first level:
        self.loadLevel(self.currentLevel)

    #--------------------------------------------------------------------------
    #      Method: loadLevel
    #
    # Description: Initializes the map, items, NPCs, and player character for a
    #              given level, then begins playing background music.
    #
    #      Inputs: level - Number corresponding to the desired level.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def loadLevel(self, level):
        # Initialize the map:
        self.map = map.Map(level,
                           self.mapTiles,
                           self.screen,
                           SCREEN_SIZE_X,
                           SCREEN_SIZE_Y)

        # Initialize items:
##        self.items = []
##        for item in ITEM_LOCATIONS[level]:
##            self.items.append(Item(item[0], # ID number
##                                   self.characterTiles,
##                                   self.map,
##                                   self.screen,
##                                   (item[1] - 1) * MAP_TILE_SIZE,
##                                   (item[2] - 1) * MAP_TILE_SIZE))

        # Initialize NPCs:
        self.NPCs = []
        for NPC in NPC_LOCATIONS[level]:
            self.NPCs.append(NonPlayerCharacter(NPC[0], # ID number
                                                self.characterTiles,
                                                self.map,
                                                self.screen,
                                                (NPC[1] - 1) * MAP_TILE_SIZE,
                                                (NPC[2] - 1) * MAP_TILE_SIZE))

        # Initialize the player:
        positionX = (STARTING_LOCATIONS[level][0] - 1) * MAP_TILE_SIZE
        positionY = (STARTING_LOCATIONS[level][1] - 1) * MAP_TILE_SIZE
        self.player = PlayerCharacter(self.characterTiles,
                                      self.map,
                                      self.screen,
                                      positionX,
                                      positionY)

        # Load and begin playing background music:
        pygame.mixer.music.load(MUSIC[level])
        pygame.mixer.music.play(-1) # Pass -1 for infinite looping.

    #--------------------------------------------------------------------------
    #      Method: gameLogic
    #
    # Description: Determines game behavior according to keyboard input and
    #              interactions among all active objects.
    #
    #      Inputs: keys    - Keys that are currently pressed down.
    #              newKeys - Keys that have just begun to be pressed down.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def gameLogic(self, keys, newKeys):
        # Check for level-completion:
        if self.player.getTileNumberBehind() == OPEN_DOOR:
            pygame.mixer.music.fadeout(MUSIC_FADEOUT_LENGTH)
            self.player.victoryPose()
            self.currentLevel += 1
            if self.currentLevel > NUM_LEVELS:
                self.currentLevel = 1
            self.loadLevel(self.currentLevel)

        # If the level is not complete, execute each character's game logic:
        else:
            self.player.gameLogic(keys, newKeys)
            for NPC in self.NPCs:
                # Check for damaging collisions with the player:
                if NPC.isOverlapping(self.player):
                    self.player.takeDamage()
                # Remove dead/departed NPCs:
                if NPC.y + NPC.heightOffset > (self.map.mapHeight * \
                                               MAP_TILE_SIZE):
                    self.NPCs.remove(NPC)
                else:
                    NPC.gameLogic()

    #--------------------------------------------------------------------------
    #      Method: paint
    #
    # Description: Draws the map and each active game object onto the screen.
    #
    #      Inputs: surface - The surface onto which everything will be drawn.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def paint(self, surface):
        # Determine the top-left pixel to be displayed:
        x = self.player.x - ((SCREEN_SIZE_X / 2) * MAP_TILE_SIZE)
        y = self.player.y - ((SCREEN_SIZE_Y / 2) * MAP_TILE_SIZE)

        # Draw the currently-visible map tiles and game characters:
        self.map.draw(x, y)
        self.player.draw()
        for NPC in self.NPCs:
            NPC.draw(x, y)

#------------------------------------------------------------------------------
#    Function: main
#
# Description: Creates and runs a 'ToadsAdventure' game. If a command-line
#              argument has been provided, it will be used to determine the
#              starting level; otherwise, the game starts at Level 1.
#
#      Inputs: None, although the starting level may be dictated as a command-
#              line argument.
#
#     Outputs: None.
#------------------------------------------------------------------------------
def main():
    # Check the command-line arguments:
    if len(sys.argv) == 2:
        startingLevel = sys.argv[1]
    else:
        startingLevel = 1

    game = ToadsAdventure(startingLevel,
                          MAP_TILESET_FILENAME,
                          CHARACTER_TILESET_FILENAME,
                          SCREEN_SIZE_X,
                          SCREEN_SIZE_Y,
                          FRAMES_PER_SECOND)
    game.mainLoop()

if __name__ == '__main__':
    main()
