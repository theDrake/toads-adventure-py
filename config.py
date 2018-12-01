#-------------------------------------------------------------------------------
#    Filename: config.py
#
#      Author: David C. Drake (https://davidcdrake.com)
#
# Description: Configuration file for Toad's Adventure.
#-------------------------------------------------------------------------------

FRAMES_PER_SECOND = 60
NUM_LEVELS = 5
MAPS = [None,
        'maps/level1.map',
        'maps/level2.map',
        'maps/level3.map',
        'maps/level4.map',
        'maps/level5.map']
MUSIC = [None,
         'music/overworld.mp3',  # Level 1
         'music/underworld.mp3', # Level 2
         'music/overworld.mp3',  # Level 3
         'music/underworld.mp3', # Level 4
         'music/overworld.mp3']  # Level 5
MUSIC_FADEOUT_LENGTH = 1000 # milliseconds
SKY_BLUE = 0x87CEEB
BISQUE = 0xFFE4C4
BLACK = 0x000000
MAP_BACKGROUNDS = [None,
                   SKY_BLUE, # Level 1
                   BLACK,    # Level 2
                   BISQUE,   # Level 3
                   BLACK,    # Level 4
                   SKY_BLUE] # Level 5
MAP_TILES_FILENAME = 'images/map_tiles.png'
CHARACTER_TILES_FILENAME = 'images/character_tiles.png'
MAP_TILE_SIZE = 64 # pixels per side
CHARACTER_TILE_SIZE = 128 # pixels per side

# tiles that don't cause collision
NON_SOLID_TILES  = frozenset([21, 22, 23, 24, 25, 26, 37, 38, 39, 44, 57, 62,
                              63, 64, 65, 72, 73, 80, 81, 82, 83, 84, 85, 86,
                              87, 88, 90, 91, 94, 95, 99, 100, 101, 102, 103,
                              104, 105, 106, 108, 111, 112, 113, 114, 126])

# tiles that cause collision only from the top
TOP_SOLID_TILES  = frozenset([3, 4, 5, 6, 7, 8, 9, 10, 11, 27, 28, 29, 40, 41,
                              42, 43, 45, 46, 47, 58, 59, 60, 61, 76, 77, 78,
                              79, 96, 130, 131])

# tiles that cause collision from any direction
SOLID_TILES = frozenset(set(range(144)) - (NON_SOLID_TILES | TOP_SOLID_TILES))

OPEN_DOOR = 62
LOCKED_DOOR = 80
SPIKE_TILE = 132
CLIMBABLE_TILES = frozenset([57, 73, 90, 91, 108])
ICY_TILES = frozenset([12, 13, 14, 15, 27, 28, 29, 30, 31, 32, 33, 48, 49, 50,
                       51, 66, 67, 68, 129])

NUM_GAME_CHARACTER_TYPES = 10
PLAYER, SHY_GUY_RED, SHY_GUY_BLUE, NINJI, FLURRY, SPARK, PORCUPO, ALBATOSS, \
    POKEY, PHANTO = range(NUM_GAME_CHARACTER_TYPES)

FIRST_PLAYER_TILE_BIG = 0
FIRST_PLAYER_TILE_SMALL = 10
FIRST_CLIMBING_TILE_BIG = 6
FIRST_CLIMBING_TILE_SMALL = 16
CROUCHING_TILE_BIG = 8
CROUCHING_TILE_SMALL = 18
PLAYER_VICTORY_TILE_BIG = 9
PLAYER_VICTORY_TILE_SMALL = 20
PLAYER_DEAD_TILE = 19
NPC_FIRST_TILES = [None,
                   22, # Shy Guy, Red
                   26, # Shy Guy, Blue
                   30, # Ninji
                   34, # Flurry
                   38, # Spark
                   41, # Porcupo
                   45, # Albatoss
                   57, # Pokey
                   61] # Phanto

# pixel offsets for width (both sides) and height (above only) of tiles
DEFAULT_WIDTH_OFFSET = 40
DEFAULT_HEIGHT_OFFSET = 52
PLAYER_WIDTH_OFFSET = 36
PLAYER_HEIGHT_OFFSET_BIG = 24
PLAYER_HEIGHT_OFFSET_SMALL = 52

# number of different stances when moving in a single direction
DEFAULT_STANCES = 2
PLAYER_STANCES = 3
SPARK_STANCES = 3
ALBATOSS_STANCES = 6
PHANTO_STANCES = 0

PLAYER_JUMPING_STANCE = 2
NINJI_JUMPING_STANCE = 1

MIN_PIXELS_PER_FRAME = 4 # all motion will round up to a multiple of this
PIXELS_PER_STANCE_CHANGE = 48
PLAYER_ACCEL_RATE = 2.0 # pixels per frame
DEFAULT_NPC_ACCEL_RATE = 1.0 # pixels per frame
DEFAULT_FRICTION_PER_FRAME = 1.0 # pixels per frame
ICE_FRICTION_PER_FRAME = 0.5 # pixels per frame
GRAVITY_PER_FRAME = 2.0 # pixels per frame
PLAYER_MAX_SPEED_X = 16.0 # pixels per frame
PLAYER_MAX_SPEED_Y = 32.0 # pixels per frame
DEFAULT_NPC_MAX_SPEED_X = 12.0 # pixels per frame
DEFAULT_NPC_MAX_SPEED_Y = 24.0 # pixels per frame
PLAYER_CLIMB_RATE = 8.0 # pixels per frame
INVINCIBILITY_AFTER_DAMAGE = 150 # game cycles

PLAYER_START_LOCATION = [None,
                         (1, 29),  # Level 1
                         (5, 19),  # Level 2
                         (5, 29),  # Level 3
                         (11, 44), # Level 4
                         (6, 32)]  # Level 5
NPC_LOCATIONS = [[],
                 # Level 1:
                 [(NINJI, 30, 38),
                  (SHY_GUY_RED, 29, 29),
                  (SHY_GUY_BLUE, 50, 34),
                  (SHY_GUY_RED, 67, 29),
                  (SHY_GUY_RED, 71, 29),
                  (SHY_GUY_RED, 75, 29),
                  (SHY_GUY_RED, 79, 29),
                  (SHY_GUY_BLUE, 150, 27),
                  (SHY_GUY_BLUE, 172, 7),
                  (NINJI, 199, 27)
                  ],
                 # Level 2:
                 [(SHY_GUY_RED, 89, 19),
                  (SHY_GUY_RED, 121, 19),
                  (SHY_GUY_RED, 132, 19),
                  (SHY_GUY_RED, 181, 19),
                  (NINJI, 52, 42),
                  (SHY_GUY_BLUE, 33, 43),
                  (SHY_GUY_BLUE, 73, 33),
                  (SHY_GUY_BLUE, 102, 35),
                  (SHY_GUY_BLUE, 115, 36),
                  (NINJI, 164, 46),
                  (SHY_GUY_BLUE, 155, 45),
                  (SHY_GUY_BLUE, 154, 42),
                  (SHY_GUY_BLUE, 155, 40),
                  (SHY_GUY_BLUE, 154, 37),
                  (SHY_GUY_BLUE, 155, 34),
                  (SHY_GUY_BLUE, 154, 32)
                  ],
                 # Level 3:
                 [(FLURRY, 19, 21),
                  (FLURRY, 41, 22),
                  (FLURRY, 89, 13),
                  (FLURRY, 102, 29),
                  (FLURRY, 159, 29),
                  (FLURRY, 178, 29),
                  (FLURRY, 193, 29),
                  ],
                 # Level 4:
                 [(PORCUPO, 41, 40),
                  (NINJI, 177, 44),
                  (NINJI, 175, 43),
                  (PORCUPO, 192, 32),
                  (SPARK, 16, 26),
                  (SPARK, 44, 27),
                  (SPARK, 62, 27),
                  (SPARK, 80, 27),
                  (SPARK, 98, 27),
                  (SHY_GUY_BLUE, 180, 9),
                  (SHY_GUY_BLUE, 160, 12),
                  (SHY_GUY_BLUE, 143, 9),
                  (SHY_GUY_BLUE, 136, 12),
                  (SHY_GUY_BLUE, 112, 9),
                  (SHY_GUY_BLUE, 104, 12),
                  (SHY_GUY_BLUE, 96, 9),
                  (SHY_GUY_BLUE, 75, 12),
                  (SHY_GUY_BLUE, 56, 9),
                  ],
                 # Level 5:
                 [(ALBATOSS, 0, 26),
                  (ALBATOSS, 133, 35),
                  (ALBATOSS, 198, 5),
                  (SHY_GUY_BLUE, 32, 40),
                  (SHY_GUY_BLUE, 43, 34),
                  (SHY_GUY_BLUE, 65, 36),
                  (SHY_GUY_BLUE, 32, 40),
                  (SHY_GUY_BLUE, 108, 40),
                  (SHY_GUY_RED, 145, 29),
                  (SHY_GUY_BLUE, 151, 23),
                  (SHY_GUY_BLUE, 198, 21),
                  (SHY_GUY_BLUE, 187, 6),
                  ]
                 ]
