#------------------------------------------------------------------------------
#    Filename: tileset.py
#
#      Author: David C. Drake (http://davidcdrake.com)
#
# Description: Handles tile images for the Toad's Adventure game. Developed
#              using Python 2.7 and PyGame 1.9.
#------------------------------------------------------------------------------

import pygame
from config import *

#------------------------------------------------------------------------------
#       Class: Tileset
#
# Description: Responsible for loading sets of tiles, providing information
#              about tiles, and mapping tile numbers to tile images.
#
#     Methods: __init__, getTile, getTileSize, getTileCoordsAt, isSolid, isIcy,
#              isClimbable, _validTileNum
#------------------------------------------------------------------------------
class Tileset:
    #--------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Initializes a tileset by loading an image file and
    #              extracting individual tile surfaces from it.
    #
    #      Inputs: filename - Name of an image file (which should contain a set
    #                         of tiles).
    #              tileSize - Length of a side of a single tile.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def __init__(self, filename, tileSize):
        # Load the image from the file and store its dimensions:
        image = pygame.image.load(filename)
        (self.imageWidth, self.imageHeight) = image.get_size()

        # Calculate the number of columns and rows in the tileset image:
        self.tileSize = tileSize
        self.cols = self.imageWidth  / self.tileSize
        self.rows = self.imageHeight / self.tileSize

        # Extract each individual tile surface from the image:
        self.tiles = []
        y = 0
        for r in range(self.rows):
            x = 0
            for c in range(self.cols):
                rect = pygame.rect.Rect(x, y, self.tileSize, self.tileSize)
                self.tiles.append(image.subsurface(rect))
                x += self.tileSize
            y += self.tileSize

    #--------------------------------------------------------------------------
    #      Method: getTile
    #
    # Description: Given a tile number, returns the corresponding tile image
    #              (in the form of a 'Rect' object).
    #
    #      Inputs: tileNum - .
    #
    #     Outputs: The tile ('Rect' object) corresponding to the tile number,
    #              or 'None' if the number is invalid.
    #--------------------------------------------------------------------------
    def getTile(self, tileNum):
        if self._validTileNum(tileNum):
            return self.tiles[tileNum]
        return None

    #--------------------------------------------------------------------------
    #      Method: getTileSize
    #
    # Description: Returns the length of one side of a tile.
    #
    #      Inputs: None.
    #
    #     Outputs: The length of one side of a tile.
    #--------------------------------------------------------------------------
    def getTileSize(self):
        return self.tileSize

    #--------------------------------------------------------------------------
    #      Method: getTileCoordsAt
    #
    # Description: Given a tuple of pixel coordinates, returns a corresponding
    #              tuple of tile-size coordinates.
    #
    #      Inputs: x - Horizontal pixel coordinate.
    #              y - Vertical pixel coordinate.
    #
    #     Outputs: A tuple containing tile-size coordinates.
    #--------------------------------------------------------------------------
    def getTileCoordsAt(self, x, y):
        return (x / self.tileSize, y / self.tileSize)

    #--------------------------------------------------------------------------
    #      Method: isSolid
    #
    # Description: Returns 'True' if the tile is completely solid.
    #
    #      Inputs: tileNum - Tile number for the tile of interest.
    #
    #     Outputs: 'True' if the tile is in the SOLID_TILES set, 'False'
    #              otherwise.
    #--------------------------------------------------------------------------
    def isSolid(self, tileNum):
        return tileNum in SOLID_TILES

    #--------------------------------------------------------------------------
    #      Method: isNonSolid
    #
    # Description: Returns 'True' if the tile is non-solid (i.e., neither solid
    #              nor top-solid).
    #
    #      Inputs: tileNum - Tile number for the tile of interest.
    #
    #     Outputs: 'True' if the tile is in the NON_SOLID_TILES set, 'False'
    #              otherwise.
    #--------------------------------------------------------------------------
    def isNonSolid(self, tileNum):
        return tileNum in NON_SOLID_TILES or tileNum is -1

    #--------------------------------------------------------------------------
    #      Method: isIcy
    #
    # Description: Returns 'True' if the tile is ice-covered.
    #
    #      Inputs: tileNum - Tile number for the tile of interest.
    #
    #     Outputs: 'True' if the tile is in the ICY_TILES set, 'False'
    #              otherwise.
    #--------------------------------------------------------------------------
    def isIcy(self, tileNum):
        return tileNum in ICY_TILES

    #--------------------------------------------------------------------------
    #      Method: isClimbable
    #
    # Description: Returns 'True' if the tile represents a climbable object.
    #
    #      Inputs: tileNum - Tile number for the tile of interest.
    #
    #     Outputs: 'True' if the tile is in the CLIMBABLE_TILES set, 'False'
    #              otherwise.
    #--------------------------------------------------------------------------
    def isClimbable(self, tileNum):
        return tileNum in CLIMBABLE_TILES

    #--------------------------------------------------------------------------
    #      Method: _validTileNum
    #
    # Description: Returns 'True' if the tile number is within the parameters
    #              of the tileset.
    #
    #      Inputs: tileNum - Tile number of interest.
    #
    #     Outputs: 'True' if the tile is valid, 'False' otherwise.
    #--------------------------------------------------------------------------
    def _validTileNum(self, tileNum):
        if tileNum < 0 or tileNum >= (self.rows * self.cols):
            return False
        return True
