#-------------------------------------------------------------------------------
#    Filename: characters.py
#
#      Author: David C. Drake (https://davidcdrake.com)
#
# Description: Manages player and non-player characters for Toad's Adventure.
#              Developed using Python 2.7 and Pygame 1.9.
#-------------------------------------------------------------------------------

import pygame
from pygame import display
import math
import random
import time
from config import *

#-------------------------------------------------------------------------------
#       Class: GameCharacter
#
# Description: Represents a game character and manages movement, collisions,
#              graphical rendering, etc.
#
#     Methods: __init__, draw, push_x, push_y, move_left, move_right,
#              apply_friction, apply_gravity, jump, move, is_colliding,
#              overlaps, will_fall, on_ground, on_ice, get_tile_number_behind,
#              get_tile_number_below, round_up
#-------------------------------------------------------------------------------
class GameCharacter:
    #---------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Initializes a character's basic stats.
    #
    #      Inputs: ID            - ID number for the game character's type.
    #              max_speed_x   - Maximum horizontal speed.
    #              max_speed_y   - Maximum vertical speed.
    #              accel_rate    - Rate of acceleration per frame, in pixels.
    #              tiles         - Tileset used by all game characters.
    #              first_tile    - Tile number of character's first tile.
    #              stances       - Number of different movement stances.
    #              width_offset  - Number of empty pixels to the character's
    #                              side in its tile images.
    #              height_offset - Number of empty pixels above the character in
    #                              its tile images.
    #              map           - The current map/level.
    #              screen        - The screen on which the game is displayed.
    #              x             - Initial x-coordinate for upper-left pixel.
    #              y             - Initial y-coordinate for upper-left pixel.
    #              facing_right  - 'True' if character should be facing right.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def __init__(self, ID, max_speed_x, max_speed_y, accel_rate, tiles,
                 first_tile, stances, width_offset, height_offset, map, screen,
                 x, y, facing_right=True):
        self.ID = ID
        self.max_speed_x = max_speed_x
        self.max_speed_y = max_speed_y
        self.accel_rate = accel_rate
        self.tiles = tiles
        self.first_tile = first_tile
        self.stances = stances
        self.width_offset = width_offset
        self.height_offset = height_offset
        self.map = map
        self.screen = screen
        self.x = x
        self.y = y
        self.facing_right = facing_right
        self.dx = 0.0 # horizontal velocity
        self.dy = 0.0 # vertical velocity
        self.current_stance = 0 # will range from 0 to "self.stances - 1"
        self.pixels_moved = 0 # helps determine when stance changes occur
        self.num_stance_changes = 0
        self.is_crouching = False
        self.is_climbing = False
        self.is_flying = False

    #---------------------------------------------------------------------------
    #      Method: push_x
    #
    # Description: Accelerates the character along the x-axis.
    #
    #      Inputs: ddx - The change to apply to character's horizontal velocity.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def push_x(self, ddx):
        self.dx += ddx
        if self.dx > 0.0:
            self.facing_right = True
            if self.dx > self.max_speed_x:
                self.dx = self.max_speed_x
        elif self.dx < 0.0:
            self.facing_right = False
            if self.dx < (self.max_speed_x * -1.0):
                self.dx = (self.max_speed_x * -1.0)

    #---------------------------------------------------------------------------
    #      Method: push_y
    #
    # Description: Accelerates the character along the y-axis.
    #
    #      Inputs: ddy - The change to apply to character's vertical velocity.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def push_y(self, ddy):
        self.dy += ddy
        if self.dy > self.max_speed_y:
            self.dy = self.max_speed_y
        elif self.dy < (self.max_speed_y * -1.0):
            self.dy = (self.max_speed_y * -1.0)

    #---------------------------------------------------------------------------
    #      Method: move_left
    #
    # Description: Manages leftward movement.
    #
    #      Inputs: modifier - Optional float value to modify acceleration.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def move_left(self, modifier = 1.0):
        self.push_x(self.accel_rate * modifier * -1.0)

    #---------------------------------------------------------------------------
    #      Method: move_right
    #
    # Description: Manages rightward movement.
    #
    #      Inputs: modifier - Optional float value to modify acceleration.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def move_right(self, modifier = 1.0):
        self.push_x(self.accel_rate * modifier)

    #---------------------------------------------------------------------------
    #      Method: apply_friction
    #
    # Description: Decreases the character's horizontal velocity when moving on
    #              solid ground. Friction is diminished while on ice.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def apply_friction(self):
        if self.is_flying:
            return
        elif self.on_ice():
            friction_per_frame = ICE_FRICTION_PER_FRAME
        else:
            friction_per_frame = DEFAULT_FRICTION_PER_FRAME
        if self.dx > 0.0:
            if self.dx - friction_per_frame < 0.0:
                self.dx == 0.0
            else:
                self.push_x(friction_per_frame * -1.0)
        elif self.dx < 0.0:
            if self.dx + friction_per_frame > 0.0:
                self.dx == 0.0
            else:
                self.push_x(friction_per_frame)

    #---------------------------------------------------------------------------
    #      Method: apply_gravity
    #
    # Description: Applies downward acceleration (up to a maximum rate) unless
    #              the character is flying or climbing.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def apply_gravity(self):
        if not self.is_climbing and not self.is_flying:
            self.push_y(GRAVITY_PER_FRAME)

    #---------------------------------------------------------------------------
    #      Method: jump
    #
    # Description: Applies upward acceleration if character's on the ground.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def jump(self):
        if self.on_ground():
            self.push_y(self.max_speed_y * -2)

    #---------------------------------------------------------------------------
    #      Method: move
    #
    # Description: Changes character's position according to its velocity along
    #              x- and y-axes, except where collision occurs. Also adjusts
    #              character's stance as appropriate.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def move(self):
        # get horizontal movement values
        abs_x = self.round_up(abs(self.dx))
        sign_x = 1
        if self.dx < 0.0:
            sign_x = -1

        # get vertical movement values
        abs_y = self.round_up(abs(self.dy))
        sign_y = 1
        if self.dy < 0.0:
            sign_y = -1

        # perform horizontal movement
        pixel_count = 0
        for x in range(abs_x):
            if self.is_colliding(self.x + (1 * sign_x), self.y):
                self.dx == 0.0
                break
            else:
                self.x += (1 * sign_x)
                pixel_count += 1

        # perform vertical movement
        for y in range(abs_y):
            if self.is_colliding(self.x, self.y + (1 * sign_y)):
                self.dy == 0.0
                break
            else:
                self.y += (1 * sign_y)

        # adjust character's stance as appropriate
        if self.stances > 1:
            self.pixels_moved += pixel_count
            if self.pixels_moved > PIXELS_PER_STANCE_CHANGE:
                self.pixels_moved = 0
                self.num_stance_changes += 1
                if self.num_stance_changes < self.stances:
                    self.current_stance += 1
                    if self.current_stance >= self.stances: # error check
                        self.current_stance = 0
                        self.num_stance_changes = 0
                    # handle ninji jump behavior here
                    if self.ID == NINJI and int(time.time()) % 2:
                        self.jump()
                else:
                    self.current_stance -= 1
                    if self.current_stance == 0:
                        self.num_stance_changes = 0
            if self.dx == 0.0: # character is not moving horizontally
                self.current_stance = 0
                self.num_stance_changes = 0
                self.pixels_moved = 0
            if not self.on_ground() and not self.ID == ALBATOSS: # in the air
                self.num_stance_changes = 0
                self.pixels_moved = 0
                if self.ID == PLAYER:
                    self.current_stance = PLAYER_JUMPING_STANCE
                elif self.ID == NINJI:
                    self.current_stance = 1

    #---------------------------------------------------------------------------
    #      Method: is_colliding
    #
    # Description: Given a set of pixel coordinates representing the character's
    #              upper-left corner, checks for overlap with a solid tile along
    #              any side (compensating for character's actual width and
    #              height) as well as contact, from above, with the top of a
    #              "top-solid" tile.
    #
    #      Inputs: x - Character tile's hypothetical leftmost pixel column.
    #              y - Character tile's hypothetical topmost pixel row.
    #
    #     Outputs: 'True' if character would collide with a solid edge at the
    #              given coordinates.
    #---------------------------------------------------------------------------
    def is_colliding(self, x, y):
        left = x + self.width_offset
        right = x + (CHARACTER_TILE_SIZE - 1) - self.width_offset
        top = y + self.height_offset
        bottom = y + (CHARACTER_TILE_SIZE - 1)
        mid_x = x + CHARACTER_TILE_SIZE / 2
        mid_y = y + CHARACTER_TILE_SIZE / 2

        if (self.map.is_solid_at(left, top) or
            self.map.is_solid_at(right, top) or
            self.map.is_solid_at(left, bottom) or
            self.map.is_solid_at(right, bottom) or
            self.map.is_solid_at(left, mid_y) or
            self.map.is_solid_at(right, mid_y) or
            self.map.is_solid_at(mid_x, top) or
            self.map.is_solid_at(mid_x, bottom)):
            return True
        elif (self.dy >= 0 and
              (self.map.get_tile_number_at(left, bottom) in TOP_SOLID_TILES or
               self.map.get_tile_number_at(right, bottom) in TOP_SOLID_TILES)):
            return True

        return False

    #---------------------------------------------------------------------------
    #      Method: overlaps
    #
    # Description: Determines whether this character is colliding with another
    #              given character.
    #
    #      Inputs: other - The other character to be tested for collision.
    #
    #     Outputs: Returns 'True' if the two characters are overlapping.
    #---------------------------------------------------------------------------
    def overlaps(self, other):
        self_left = self.x + self.width_offset
        self_right = self.x + (CHARACTER_TILE_SIZE - 1) - self.width_offset
        self_top = self.y + self.height_offset
        self_bottom = self.y + (CHARACTER_TILE_SIZE - 1)

        other_left = other.x + other.width_offset
        other_right = other.x + (CHARACTER_TILE_SIZE - 1) - other.width_offset
        other_top = other.y + other.height_offset
        other_bottom = other.y + (CHARACTER_TILE_SIZE - 1)

        return (self_right >= other_left and self_left <= other_right and
                self_top <= other_bottom and self_bottom >= other_top)

    #---------------------------------------------------------------------------
    #      Method: will_fall
    #
    # Description: Determines whether the character's about to fall off a ledge.
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if character's on a solid surface next to a ledge.
    #---------------------------------------------------------------------------
    def will_fall(self):
        left = self.x
        right = self.x + CHARACTER_TILE_SIZE + 1 # - self.width_offset
        bottom = self.y + CHARACTER_TILE_SIZE + 1
        return self.on_ground() and (
            (self.facing_right and self.map.is_non_solid_at(right, bottom)) or
            (not self.facing_right and self.map.is_non_solid_at(left, bottom)))

    #---------------------------------------------------------------------------
    #      Method: on_ground
    #
    # Description: Determines whether the character's feet are on solid ground.
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if character's feet are on a solid or top-solid tile.
    #---------------------------------------------------------------------------
    def on_ground(self):
        return self.is_colliding(self.x, self.y + 1)

    #---------------------------------------------------------------------------
    #      Method: on_ice
    #
    # Description: Determines whether character's feet are on an icy tile.
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if character's feet are directly above an icy tile.
    #---------------------------------------------------------------------------
    def on_ice(self):
        return self.get_tile_number_below() in ICY_TILES

    #---------------------------------------------------------------------------
    #      Method: get_tile_number_behind
    #
    # Description: Returns tile number corresponding to map tile directly behind
    #              the character (i.e., "background" tile).
    #
    #      Inputs: None.
    #
    #     Outputs: Tile number of map tile behind the character.
    #---------------------------------------------------------------------------
    def get_tile_number_behind(self):
        return self.map.get_tile_number_at(self.x + CHARACTER_TILE_SIZE / 2,
                                           self.y + CHARACTER_TILE_SIZE - 1)

    #---------------------------------------------------------------------------
    #      Method: get_tile_number_below
    #
    # Description: Returns tile number corresponding to map tile directly below
    #              the character (i.e., one pixel lower than character's lowest
    #              pixel at its midpoint).
    #
    #      Inputs: None.
    #
    #     Outputs: Tile number of map tile underneath the character.
    #---------------------------------------------------------------------------
    def get_tile_number_below(self):
        return self.map.get_tile_number_at(self.x + CHARACTER_TILE_SIZE / 2,
                                           self.y + CHARACTER_TILE_SIZE + 1)

    #---------------------------------------------------------------------------
    #      Method: round_up
    #
    # Description: Given a floating point value, returns the nearest greater or
    #              equal integer in intervals of MIN_PIXELS_PER_FRAME.
    #
    #      Inputs: n - Floating point value to be rounded up.
    #
    #     Outputs: The rounded-up integer value.
    #---------------------------------------------------------------------------
    def round_up(self, n):
        minimum = MIN_PIXELS_PER_FRAME
        return ((int(math.ceil(n)) + (minimum - 1)) / minimum) * minimum

#-------------------------------------------------------------------------------
#       Class: PlayerCharacter
#
# Description: Represents the player character.
#
#     Methods: __init__, game_logic, draw, is_big, is_small, grow, shrink,
#              is_invincible, climb, climb_up, climb_down, can_climb,
#              take_damage, pose_and_pause, victory_pose, die
#-------------------------------------------------------------------------------
class PlayerCharacter(GameCharacter):
    #---------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Initializes the player character's basic stats.
    #
    #      Inputs: tiles  - Tileset used by all game characters.
    #              map    - The current map/level.
    #              screen - The screen on which the game is displayed.
    #              x      - Initial x-coordinate for upper-left pixel.
    #              y      - Initial y-coordinate for upper-left pixel.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def __init__(self, tiles, map, screen, x, y):
        GameCharacter.__init__(self, PLAYER, PLAYER_MAX_SPEED_X,
                               PLAYER_MAX_SPEED_Y, PLAYER_ACCEL_RATE, tiles,
                               FIRST_PLAYER_TILE_BIG, PLAYER_STANCES,
                               PLAYER_WIDTH_OFFSET, PLAYER_HEIGHT_OFFSET_BIG,
                               map, screen, x, y)
        self.invincibility_timer = 0
        self.climbing_stance = 0

    #---------------------------------------------------------------------------
    #      Method: game_logic
    #
    # Description: Determines player character's behavior according to keyboard
    #              input and interactions among all active game objects.
    #
    #      Inputs: keys     - Keys currently pressed down.
    #              new_keys - Keys that have just begun to be pressed down.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def game_logic(self, keys, new_keys):
        # check for damage and death
        if self.get_tile_number_below() == SPIKE_TILE:
            self.take_damage()
        elif self.y + self.height_offset > (self.map.map_height *
                                            MAP_TILE_SIZE):
            self.die()

        # check invincibility timer
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

        # check crouching/climbing status
        if (self.is_crouching and pygame.K_DOWN not in keys and
            pygame.K_s not in keys):
            self.is_crouching = False
        if self.is_climbing:
            if not self.can_climb():
                self.is_climbing = False
            else:
                self.dy = 0.0

        # horizontal acceleration
        if self.on_ground():
            self.apply_friction()
            if not self.is_crouching:
                if pygame.K_LEFT in keys or pygame.K_a in keys:
                    self.move_left()
                if pygame.K_RIGHT in keys or pygame.K_d in keys:
                    self.move_right()
        else:
            if pygame.K_LEFT in keys or pygame.K_a in keys:
                self.move_left(0.5)
            if pygame.K_RIGHT in keys or pygame.K_d in keys:
                self.move_right(0.5)

        # vertical acceleration
        self.apply_gravity()
        if pygame.K_SPACE in new_keys:
            self.jump()

        # climbing
        if (pygame.K_UP in keys or pygame.K_w in keys) and self.can_climb():
            self.climb_up()
        elif (pygame.K_DOWN in keys or pygame.K_s in keys) and self.can_climb():
            self.climb_down()

        # crouching
        if pygame.K_DOWN in keys or pygame.K_s in keys:
            self.is_crouching = True

        # apply motion
        self.move()

    #---------------------------------------------------------------------------
    #      Method: draw
    #
    # Description: Draws the player character on the screen.
    #
    #      Inputs: position - Tuple containing (x, y) pixel coordinates.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def draw(self, position):
        if self.is_invincible() and random.randint(0, 1): # flicker effect
            return
        elif self.is_climbing:
            if self.is_big():
                self.screen.blit(self.tiles.get_image(
                                     FIRST_CLIMBING_TILE_BIG +
                                     self.climbing_stance),
                                 position)
            else:
                self.screen.blit(self.tiles.get_image(
                                     FIRST_CLIMBING_TILE_SMALL +
                                     self.climbing_stance),
                                 position)
        elif self.is_crouching:
            if self.is_big():
                self.screen.blit(self.tiles.get_image(CROUCHING_TILE_BIG),
                                 position)
            else:
                self.screen.blit(self.tiles.get_image(CROUCHING_TILE_SMALL),
                                 position)
        elif self.facing_right:
            self.screen.blit(self.tiles.get_image(self.first_tile +
                                                  self.current_stance),
                             position)
        else: # facing left
            self.screen.blit(self.tiles.get_image(self.first_tile +
                                                  self.stances +
                                                  self.current_stance),
                             position)

    #---------------------------------------------------------------------------
    #      Method: is_big
    #
    # Description: Determines whether Toad is "big" (full health).
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if the character has full health, 'False' otherwise.
    #---------------------------------------------------------------------------
    def is_big(self):
        return self.first_tile == FIRST_PLAYER_TILE_BIG

    #---------------------------------------------------------------------------
    #      Method: is_small
    #
    # Description: Determines whether Toad is "small" (not full health).
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if the character's taken damage, 'False' otherwise.
    #---------------------------------------------------------------------------
    def is_small(self):
        return self.first_tile == FIRST_PLAYER_TILE_SMALL

    #---------------------------------------------------------------------------
    #      Method: grow
    #
    # Description: Makes Toad "big" (restores full health).
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def grow(self):
        self.first_tile = FIRST_PLAYER_TILE_BIG
        self.height_offset = PLAYER_HEIGHT_OFFSET_BIG

    #---------------------------------------------------------------------------
    #      Method: shrink
    #
    # Description: Makes Toad "small" (one more hit = death).
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def shrink(self):
        self.first_tile = FIRST_PLAYER_TILE_SMALL
        self.height_offset = PLAYER_HEIGHT_OFFSET_SMALL

    #---------------------------------------------------------------------------
    #      Method: is_invincible
    #
    # Description: Determines whether player is currently invincible.
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if the character's invincible.
    #---------------------------------------------------------------------------
    def is_invincible(self):
        return self.invincibility_timer > 0

    #---------------------------------------------------------------------------
    #      Method: climb
    #
    # Description: Causes player to move in a given vertical direction according
    #              to climbing rate.
    #
    #      Inputs: direction - The direction in which to climb: positive for
    #                          upward movement, negative for downward.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def climb(self, direction):
        if not self.is_climbing:
            self.is_climbing = True
            self.dx = 0.0
            self.dy = 0.0
        self.dy = PLAYER_CLIMB_RATE * direction
        if random.randint(0, 8) == 0:
            self.climbing_stance += 1
            if self.climbing_stance > 1:
                self.climbing_stance = 0

    #---------------------------------------------------------------------------
    #      Method: climb_up
    #
    # Description: Causes Toad to climb upwards.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def climb_up(self):
        self.climb(-1)

    #---------------------------------------------------------------------------
    #      Method: climb_down
    #
    # Description: Causes Toad to climb downwards.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def climb_down(self):
        self.climb(1)

    #---------------------------------------------------------------------------
    #      Method: can_climb
    #
    # Description: Determines whether Toad can climb based on the tile directly
    #              behind him.
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if Toad can climb, 'False' otherwise.
    #---------------------------------------------------------------------------
    def can_climb(self):
        return self.get_tile_number_behind() in CLIMBABLE_TILES

    #---------------------------------------------------------------------------
    #      Method: take_damage
    #
    # Description: Causes Toad to take damage. If Toad was big, he's now small
    #              and temporarily invincible. If Toad was small, he's now dead.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def take_damage(self):
        if not self.is_invincible():
            if self.is_small():
                self.die()
            else:
                self.shrink()
                self.invincibility_timer = INVINCIBILITY_AFTER_DAMAGE

    #---------------------------------------------------------------------------
    #      Method: pose_and_pause
    #
    # Description: Displays Toad in a given pose for a given number of seconds
    #              (during which everything will be paused).
    #
    #      Inputs: pose  - Tile number of desired pose.
    #              pause - Pause duration, in seconds.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def pose_and_pause(self, pose, pause):
        # draw map again to erase player's previous tile
        x = self.x - (self.map.screen_width / 2)
        y = self.y - (self.map.screen_height / 2)
        self.map.draw(x, y)

        # draw desired pose, then pause the game
        position = (self.map.screen_width / 2 - MAP_TILE_SIZE,
                    self.map.screen_height / 2 - MAP_TILE_SIZE)
        self.screen.blit(self.tiles.get_image(pose), position)
        display.flip()
        time.sleep(pause)

    #---------------------------------------------------------------------------
    #      Method: victory_pose
    #
    # Description: Determines appropriate victory pose and temporarily pauses
    #              the game while displaying it.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def victory_pose(self):
        if self.is_big():
            pose = PLAYER_VICTORY_TILE_BIG       # big, facing 4th wall
        elif self.facing_right:
            pose = PLAYER_VICTORY_TILE_SMALL     # small, facing right
        else:
            pose = PLAYER_VICTORY_TILE_SMALL + 1 # small, facing left
        self.pose_and_pause(pose, 1)

    #---------------------------------------------------------------------------
    #      Method: die
    #
    # Description: Handles Toad's death and respawns him at starting point.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def die(self):
        self.pose_and_pause(PLAYER_DEAD_TILE, 1)
        self.grow()
        self.facing_right = True
        (self.x, self.y) = self.map.player_start_location
        (self.dx, self.dy) = (0, 0)

#-------------------------------------------------------------------------------
#       Class: NonPlayerCharacter
#
# Description: Represents an NPC.
#
#     Methods: __init__, game_logic, draw
#-------------------------------------------------------------------------------
class NonPlayerCharacter(GameCharacter):
    #---------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Initializes the NPC's basic stats.
    #
    #      Inputs: ID           - ID number for the NPC's type.
    #              tiles        - Tileset used by all game characters.
    #              map          - The current map/level.
    #              screen       - The screen on which the game is displayed.
    #              x            - Initial x-coordinate for upper-left pixel.
    #              y            - Initial y-coordinate for upper-left pixel.
    #              facing_right - 'True' if character should be facing right.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def __init__(self, ID, tiles, map, screen, x, y, facing_right=False):
        max_speed_x = DEFAULT_NPC_MAX_SPEED_X
        max_speed_y = DEFAULT_NPC_MAX_SPEED_Y
        accel_rate = DEFAULT_NPC_ACCEL_RATE
        width_offset = DEFAULT_WIDTH_OFFSET
        height_offset = DEFAULT_HEIGHT_OFFSET
        first_tile = NPC_FIRST_TILES[ID]
        stances = DEFAULT_STANCES
        if ID == SPARK:
            stances = SPARK_STANCES
        elif ID == ALBATOSS:
            stances = ALBATOSS_STANCES
        elif ID == PHANTO:
            stances = PHANTO_STANCES
        elif ID == FLURRY:
            max_speed_x *= 1.5
        GameCharacter.__init__(self, ID, max_speed_x, max_speed_y, accel_rate,
                               tiles, first_tile, stances, width_offset,
                               height_offset, map, screen, x, y, facing_right)
        if ID == SPARK or ID == ALBATOSS or ID == PHANTO:
            self.is_flying = True

    #---------------------------------------------------------------------------
    #      Method: game_logic
    #
    # Description: Determines NPC behavior according to interactions among all
    #              active game objects.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def game_logic(self):
        # check for change in orientation
        if ((self.facing_right and
             self.is_colliding(self.x + CHARACTER_TILE_SIZE -
                               self.width_offset * 3, self.y))                or
            (not self.facing_right and self.is_colliding(self.x - 1, self.y)) or
            (self.is_flying and ((not self.facing_right and self.x - 1 <= 0)  or
                                 (self.facing_right and self.x +
                                  CHARACTER_TILE_SIZE -
                                  self.width_offset * 2 >=
                                  self.map.get_size()[0] * MAP_TILE_SIZE)))   or
            (self.ID == SHY_GUY_BLUE and self.will_fall())):
            self.facing_right = not self.facing_right
            self.dx *= -1.0

        # horizontal acceleration
        self.apply_friction()
        if self.facing_right:
            self.move_right()
        else:
            self.move_left()

        # vertical acceleration
        self.apply_gravity()

        # apply motion
        self.move()

    #---------------------------------------------------------------------------
    #      Method: draw
    #
    # Description: Draws the NPC on the screen, if currently visible.
    #
    #      Inputs: map_x - Left-most map pixel currently displayed.
    #              map_y - Top-most map pixel currently displayed.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def draw(self, map_x, map_y):
        if (self.x < map_x or self.x > (map_x + self.map.screen_width) or
            self.y < map_y or self.y > (map_y + self.map.screen_height)):
            return
        position = (self.x - map_x - MAP_TILE_SIZE,
                    self.y - map_y - MAP_TILE_SIZE)
        if self.ID == SPARK or self.facing_right:
            self.screen.blit(self.tiles.get_image(self.first_tile +
                                                  self.current_stance),
                             position)
        else: # facing left
            self.screen.blit(self.tiles.get_image(self.first_tile +
                                                  self.stances +
                                                  self.current_stance),
                             position)
