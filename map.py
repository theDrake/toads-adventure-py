#-------------------------------------------------------------------------------
#    Filename: map.py
#
#      Author: David C. Drake (https://davidcdrake.com)
#
# Description: Handles maps/levels for Toad's Adventure. Developed using Python
#              2.7 and Pygame 1.9.
#-------------------------------------------------------------------------------

import pygame
from config import *

#-------------------------------------------------------------------------------
#       Class: Map
#
# Description: A rectangular grid of tiles representing a game map/level.
#
#     Methods: __init__, get_size, get_tile_number, get_tile_number_at,
#              get_tile, is_solid_at, is_non_solid_at, draw
#-------------------------------------------------------------------------------
class Map:
    #---------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Sets up a map/level by reading a map file.
    #
    #      Inputs: level         - Number corresponding to the desired level.
    #              tiles         - Tileset object to supply tile images.
    #              screen        - Surface object for rendering the map.
    #              screen_width  - Total display width, in pixels.
    #              screen_height - Total display height, in pixels.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def __init__(self, level, tiles, screen, screen_width, screen_height):
        if level < 1 or level > NUM_LEVELS:
            level = 1
        self.tiles = tiles
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height

        fileIn = open(MAPS[level], 'r')
        self.map = eval(fileIn.read())
        fileIn.close()

        self.map_height = len(self.map)
        lowest_map_width = len(self.map[0])
        for i in range(self.map_height):
            map_width = len(self.map[i])
            if map_width != lowest_map_width: # rows should have equal length
                print('Error in row %d of %s (length %d)' % (i, MAPS[level],
                      map_width))
                if map_width < lowest_map_width:
                    lowest_map_width = map_width
        self.map_width = lowest_map_width

        self.bg_color = pygame.Color(MAP_BACKGROUNDS[level])
        self.player_start_location = (
            (PLAYER_START_LOCATION[level][0] - 1) * MAP_TILE_SIZE,
            (PLAYER_START_LOCATION[level][1] - 1) * MAP_TILE_SIZE)

    #---------------------------------------------------------------------------
    #      Method: get_size
    #
    # Description: Returns map width and height in tuple form.
    #
    #      Inputs: None.
    #
    #     Outputs: A tuple containing the map's width and height.
    #---------------------------------------------------------------------------
    def get_size(self):
        return (self.map_width, self.map_height)

    #---------------------------------------------------------------------------
    #      Method: get_tile_number
    #
    # Description: Given the tile coordinates for a location, returns a
    #              corresponding tile number.
    #
    #      Inputs: x - Horizontal coordinate, measured in tile blocks.
    #              y - Vertical coordinate, measured in tile blocks.
    #
    #     Outputs: Tile number for the location in question (or -1 if the
    #              coordinates are invalid).
    #---------------------------------------------------------------------------
    def get_tile_number(self, x, y):
        if x < 0 or y < 0 or x >= self.map_width or y >= self.map_height:
            return -1
        return self.map[y][x] # y == row, x == column

    #---------------------------------------------------------------------------
    #      Method: get_tile_number_at
    #
    # Description: Given the pixel coordinates for a location, returns a
    #              corresponding tile number.
    #
    #      Inputs: x - Horizontal coordinate, measured in pixels.
    #              y - Vertical coordinate, measured in pixels.
    #
    #     Outputs: Tile number for the location in question (or -1 if the
    #              coordinates are invalid).
    #---------------------------------------------------------------------------
    def get_tile_number_at(self, x, y):
        (newX, newY) = self.tiles.get_tile_coords_at(x, y)
        return self.get_tile_number(newX, newY)

    #---------------------------------------------------------------------------
    #      Method: get_tile
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
    #---------------------------------------------------------------------------
    def get_tile(self, x, y):
        if y >= self.map_height and x >= 0 and x < self.map_width:
            y = self.map_height - 1
        tile_num = self.get_tile_number(x, y)
        return self.tiles.get_image(tile_num)

    #---------------------------------------------------------------------------
    #      Method: is_solid_at
    #
    # Description: Determines whether a given location is fully solid (not just
    #              top-solid).
    #
    #      Inputs: x - Horizontal coordinate, measured in pixels.
    #              y - Vertical coordinate, measured in pixels.
    #
    #     Outputs: 'True' if the location is solid.
    #---------------------------------------------------------------------------
    def is_solid_at(self, x, y):
        tile_num = self.get_tile_number_at(x, y)
        return tile_num in SOLID_TILES

    #---------------------------------------------------------------------------
    #      Method: is_non_solid_at
    #
    # Description: Determines whether a given location is non-solid (neither
    #              solid nor top-solid).
    #
    #      Inputs: x - Horizontal coordinate, measured in pixels.
    #              y - Vertical coordinate, measured in pixels.
    #
    #     Outputs: 'True' if the location is non-solid.
    #---------------------------------------------------------------------------
    def is_non_solid_at(self, x, y):
        tile_num = self.get_tile_number_at(x, y)
        return tile_num in NON_SOLID_TILES or tile_num is -1

    #---------------------------------------------------------------------------
    #      Method: draw
    #
    # Description: Draws the currently-visible part of the map onto the screen.
    #
    #      Inputs: left_col - Pixel coordinate for first column to draw.
    #              top_row  - Pixel coordinate for first row to draw.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def draw(self, left_col, top_row):
        self.screen.fill(self.bg_color)
        top_left_tile_x = left_col / MAP_TILE_SIZE
        top_left_tile_y = top_row  / MAP_TILE_SIZE
        pixel_offset_x = left_col % MAP_TILE_SIZE
        pixel_offset_y = top_row  % MAP_TILE_SIZE
        for screen_y in range(self.screen_height / MAP_TILE_SIZE + 2):
            map_y = screen_y + top_left_tile_y + 1
            for screen_x in range(self.screen_width / MAP_TILE_SIZE + 1):
                map_x = screen_x + top_left_tile_x + 1
                tile = self.get_tile(map_x, map_y)
                if tile:
                    position = ((screen_x * MAP_TILE_SIZE) - pixel_offset_x,
                                (screen_y * MAP_TILE_SIZE) - pixel_offset_y)
                    self.screen.blit(tile, position)
