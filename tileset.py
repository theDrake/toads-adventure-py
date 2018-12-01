#-------------------------------------------------------------------------------
#    Filename: tileset.py
#
#      Author: David C. Drake (https://davidcdrake.com)
#
# Description: Handles tile images for the Toad's Adventure game. Developed
#              using Python 2.7 and PyGame 1.9.
#-------------------------------------------------------------------------------

from pygame import image, rect
from config import *

#-------------------------------------------------------------------------------
#       Class: Tileset
#
# Description: Responsible for preparing and providing tile images.
#
#     Methods: __init__, get_image, get_tile_coords_at, _is_valid_tile_num
#-------------------------------------------------------------------------------
class Tileset:
    #---------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Loads an image file and extracts tile surfaces from it.
    #
    #      Inputs: filename  - Name of an image file.
    #              tile_size - Length of a side of a single tile.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def __init__(self, filename, tile_size):
        tileset_image = image.load(filename)
        (self.image_width, self.image_height) = tileset_image.get_size()
        self.tile_size = tile_size
        self.cols = self.image_width  / self.tile_size
        self.rows = self.image_height / self.tile_size
        self.tiles = []
        y = 0
        for r in range(self.rows):
            x = 0
            for c in range(self.cols):
                tile_rect = rect.Rect(x, y, self.tile_size, self.tile_size)
                self.tiles.append(tileset_image.subsurface(tile_rect))
                x += self.tile_size
            y += self.tile_size

    #---------------------------------------------------------------------------
    #      Method: get_image
    #
    # Description: Given a tile number, returns the corresponding tile image in
    #              the form of a 'Rect' object.
    #
    #      Inputs: tile_num - Tile number of interest.
    #
    #     Outputs: The 'Rect' object corresponding to the tile number (or 'None'
    #              if the number is invalid).
    #---------------------------------------------------------------------------
    def get_image(self, tile_num):
        if self._is_valid_tile_num(tile_num):
            return self.tiles[tile_num]
        return None

    #---------------------------------------------------------------------------
    #      Method: get_tile_coords_at
    #
    # Description: Given a tuple of pixel coordinates, returns a corresponding
    #              tuple of tile coordinates.
    #
    #      Inputs: x - Horizontal pixel coordinate.
    #              y - Vertical pixel coordinate.
    #
    #     Outputs: A tuple containing tile coordinates.
    #---------------------------------------------------------------------------
    def get_tile_coords_at(self, x, y):
        return (x / self.tile_size, y / self.tile_size)

    #---------------------------------------------------------------------------
    #      Method: _is_valid_tile_num
    #
    # Description: Returns 'True' if tile number's within tileset parameters.
    #
    #      Inputs: tile_num - Tile number of interest.
    #
    #     Outputs: 'True' if the tile number is valid.
    #---------------------------------------------------------------------------
    def _is_valid_tile_num(self, tile_num):
        if tile_num < 0 or tile_num >= (self.rows * self.cols):
            return False
        return True
