#------------------------------------------------------------------------------
#    Filename: map.py
#
#      Author: David C. Drake (http://davidcdrake.com)
#
# Description: Handles maps (i.e., levels) for the Toad's Adventure game.
#              Developed using Python 2.7 and PyGame 1.9.
#------------------------------------------------------------------------------

import pygame
from config import *

#------------------------------------------------------------------------------
#       Class: Map
#
# Description: A rectangular grid of tiles representing a game map/level.
#
#     Methods: __init__, getSize, getScreenSize, getTileNumber,
#              getTileNumberAt, getTile, isSolidAt, draw
#------------------------------------------------------------------------------
class Map:
    #--------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Initializes the map/level by reading a map file.
    #
    #      Inputs: level        - Number corresponding to the current level.
    #              tiles        - Tileset object to supply tile images.
    #              screen       - Surface object that will render the map.
    #              screenWidth  - Width of the game screen (in tiles).
    #              screenHeight - Height of the game screen (in tiles).
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def __init__(self, level, tiles, screen, screenWidth, screenHeight):
        self.tiles = tiles
        self.screen = screen
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        # Read map data from file:
        fileIn = open(MAPS[level], 'r')
        self.map = eval(fileIn.read())
        fileIn.close()

        # Determine map width/height (all rows should be of equal length):
        self.mapHeight = len(self.map)
        lowestMapWidth = len(self.map[0])
        for i in range(self.mapHeight):
            mapWidth = len(self.map[i])
            if mapWidth != lowestMapWidth:
                print 'Error in row %d of %s (length )' % (i,
                                                           MAPS[level],
                                                           mapWidth)
                if mapWidth < lowestMapWidth:
                    lowestMapWidth = mapWidth
        self.mapWidth = lowestMapWidth

        # Determine background color:
        self.bgColor = pygame.Color(MAP_BACKGROUNDS[level])

        # Determine player's starting location:
        self.playerStartingPosition = ((STARTING_LOCATIONS[level][0] - 1) *
                                       MAP_TILE_SIZE,
                                       (STARTING_LOCATIONS[level][1] - 1) *
                                       MAP_TILE_SIZE)

    #--------------------------------------------------------------------------
    #      Method: getSize
    #
    # Description: Returns the width and height of the map, in tuple form.
    #
    #      Inputs: None.
    #
    #     Outputs: A tuple containing the map's width and height.
    #--------------------------------------------------------------------------
    def getSize(self):
        return (self.mapWidth, self.mapHeight)

    #--------------------------------------------------------------------------
    #      Method: getTileNumber
    #
    # Description: Given the (x, y) coordinates for a location, measured in
    #              tile blocks (rather than pixels), return its tile number.
    #
    #      Inputs: x - Horizontal coordinate, measured in tile blocks.
    #              y - Vertical coordinate, measured in tile blocks.
    #
    #     Outputs: Tile number for the location in question (or -1 if the
    #              coordinates are invalid).
    #--------------------------------------------------------------------------
    def getTileNumber(self, x, y):
        if x < 0 or y < 0 or x >= self.mapWidth or y >= self.mapHeight:
            return -1
        return self.map[y][x] # y == row, x == column

    #--------------------------------------------------------------------------
    #      Method: getTileNumberAt
    #
    # Description: Given the (x, y) coordinates for a location, measured in
    #              pixels (rather than tile blocks), return its tile number.
    #
    #      Inputs: x - Horizontal coordinate, measured in pixels.
    #              y - Vertical coordinate, measured in pixels.
    #
    #     Outputs: Tile number for the location in question (or -1 if the
    #              coordinates are invalid).
    #--------------------------------------------------------------------------
    def getTileNumberAt(self, x, y):
        (newX, newY) = self.tiles.getTileCoordsAt(x, y)
        return self.getTileNumber(newX, newY)

    #--------------------------------------------------------------------------
    #      Method: getTile
    #
    # Description: Given the (x, y) coordinates for a location, measured in
    #              tile blocks (rather than pixels), return its tile image. (If
    #              the coordinates lie below the map, but within its horizontal
    #              boundaries, the nearest tile above those coordinates will be
    #              returned.)
    #
    #      Inputs: x - Horizontal coordinate, measured in tile blocks.
    #              y - Vertical coordinate, measured in tile blocks.
    #
    #     Outputs: Tile image for the location in question.
    #--------------------------------------------------------------------------
    def getTile(self, x, y):
        if y >= self.mapHeight and x >= 0 and x < self.mapWidth:
            y = self.mapHeight - 1
        tileNum = self.getTileNumber(x, y)
        return self.tiles.getTile(tileNum)

    #--------------------------------------------------------------------------
    #      Method: isSolidAt
    #
    # Description: Determines whether a given location is solid.
    #
    #      Inputs: x - Horizontal coordinate, measured in pixels.
    #              y - Vertical coordinate, measured in pixels.
    #
    #     Outputs: 'True' if the location is solid, 'False' otherwise.
    #--------------------------------------------------------------------------
    def isSolidAt(self, x, y):
        tileNum = self.getTileNumberAt(x, y)
        return self.tiles.isSolid(tileNum)

    #--------------------------------------------------------------------------
    #      Method: isNonSolidAt
    #
    # Description: Determines whether a given location is non-solid (neither
    #              solid nor top-solid).
    #
    #      Inputs: x - Horizontal coordinate, measured in pixels.
    #              y - Vertical coordinate, measured in pixels.
    #
    #     Outputs: 'True' if the location is non-solid, 'False' otherwise.
    #--------------------------------------------------------------------------
    def isNonSolidAt(self, x, y):
        tileNum = self.getTileNumberAt(x, y)
        return self.tiles.isNonSolid(tileNum)

    #--------------------------------------------------------------------------
    #      Method: draw
    #
    # Description: Draws the currently-visible part of the map onto the screen.
    #
    #      Inputs: leftCol - Pixel coordinate for the first column to be
    #                        displayed (i.e., the far left column).
    #              topRow  - Pixel coordinate for the first row to be displayed
    #                        (i.e., the top row).
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def draw(self, leftCol, topRow):
        # Apply the background color:
        self.screen.fill(self.bgColor)

        # Determine coordinates for the top-left tile, measured in tile blocks:
        topLeftTileX = leftCol / MAP_TILE_SIZE
        topLeftTileY = topRow  / MAP_TILE_SIZE

        # Determine the offset from the tile's origin, measured in pixels:
        pixelOffsetX = leftCol % MAP_TILE_SIZE
        pixelOffsetY = topRow  % MAP_TILE_SIZE

        # Draw each visible tile:
        for screenY in range(SCREEN_SIZE_Y + 1):
            mapY = screenY + topLeftTileY + 1
            for screenX in range(SCREEN_SIZE_X + 1):
                mapX = screenX + topLeftTileX + 1
                tile = self.getTile(mapX, mapY)
                if tile:
                    position = ((screenX * MAP_TILE_SIZE) - pixelOffsetX,
                                (screenY * MAP_TILE_SIZE) - pixelOffsetY)
                    self.screen.blit(tile, position)
