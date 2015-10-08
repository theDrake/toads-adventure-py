#------------------------------------------------------------------------------
#    Filename: characters.py
#
#      Author: David C. Drake (http://davidcdrake.com)
#
# Description: Manages game characters (player and non-player) for the Toad's
#              Adventure game. Developed using Python 2.7 and PyGame 1.9.
#------------------------------------------------------------------------------

import pygame
import math
import time
import random
from config import *

#------------------------------------------------------------------------------
#       Class: GameCharacter
#
# Description: Represents a game character and manages movement, collisions,
#              graphical rendering, etc.
#------------------------------------------------------------------------------
class GameCharacter:
    #--------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Initializes a character's basic stats.
    #
    #      Inputs: ID               - ID number for the game character's type.
    #              maxSpeedX        - Maximum horizontal speed.
    #              maxSpeedY        - Maximum vertical speed.
    #              accelerationRate - Rate of accel. per frame, in pixels.
    #              tiles            - The game character tileset.
    #              firstTile        - Tile number of the character's first tile
    #                                 within the tileset.
    #              stances          - Number of different movement stances.
    #              widthOffset      - Number of empty pixels to the side of the
    #                                 character (within its tile images).
    #              heightOffset     - Number of empty pixels above the
    #                                 character (within its tile images).
    #              map              - The current map/level.
    #              screen           - The screen on which to display the game.
    #              x                - Initial x-coordinate for the game
    #                                 character tile's upper-left pixel.
    #              y                - Initial y-coordinate for the game
    #                                 character tile's upper-left pixel.
    #              facingRight      - 'True' if the character should start out
    #                                 facing right.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def __init__(self,
                 ID,
                 maxSpeedX,
                 maxSpeedY,
                 accelerationRate,
                 tiles,
                 firstTile,
                 stances,
                 widthOffset,
                 heightOffset,
                 map,
                 screen,
                 x,
                 y,
                 facingRight=True):
        self.ID               = ID
        self.maxSpeedX        = maxSpeedX
        self.maxSpeedY        = maxSpeedY
        self.accelerationRate = accelerationRate
        self.tiles            = tiles
        self.firstTile        = firstTile
        self.stances          = stances
        self.widthOffset      = widthOffset
        self.heightOffset     = heightOffset
        self.map              = map
        self.screen           = screen
        self.x                = x
        self.y                = y
        self.facingRight      = facingRight

        # Horizontal and vertical velocity:
        self.dx = 0.0
        self.dy = 0.0

        # Stance values may range from 0 to "self.stances - 1":
        self.currentStance = 0

        # To track the number of movements while in current stance:
        self.moveCount = 0

        # Additional movement/stance-related values:
        self.isCrouching = False
        self.isClimbing  = False
        self.isFlying    = False

    #--------------------------------------------------------------------------
    #      Method: pushX
    #
    # Description: Accelerates the character along the x-axis.
    #
    #      Inputs: ddx - Horizontal acceleration (the change to apply to the
    #                    character's horizontal velocity).
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def pushX(self, ddx):
        self.dx += ddx
        if self.dx > 0.0:
            self.facingRight = True
            if self.dx > self.maxSpeedX:
                self.dx = self.maxSpeedX
        elif self.dx < 0.0:
            self.facingRight = False
            if self.dx < (self.maxSpeedX * -1.0):
                self.dx = (self.maxSpeedX * -1.0)

    #--------------------------------------------------------------------------
    #      Method: pushY
    #
    # Description: Accelerates the character along the y-axis.
    #
    #      Inputs: ddy - Vertical acceleration (the change to apply to the
    #                    character's vertical velocity).
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def pushY(self, ddy):
        self.dy += ddy
        if self.dy > self.maxSpeedY:
            self.dy = self.maxSpeedY
        elif self.dy < (self.maxSpeedY * -1.0):
            self.dy = (self.maxSpeedY * -1.0)

    #--------------------------------------------------------------------------
    #      Method: left
    #
    # Description: Manages leftward movement.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def left(self):
        self.pushX(self.accelerationRate * -1.0)

    #--------------------------------------------------------------------------
    #      Method: right
    #
    # Description: Manages rightward movement.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def right(self):
        self.pushX(self.accelerationRate)

    #--------------------------------------------------------------------------
    #      Method: applyFriction
    #
    # Description: Decreases the character's horizontal velocity when moving on
    #              solid ground. Friction is diminished while on ice.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def applyFriction(self):
        if self.isFlying:
            return
        frictionPerFrame = DEFAULT_FRICTION_PER_FRAME
        if self.onIce():
            frictionPerFrame = ICE_FRICTION_PER_FRAME
        if self.dx > 0.0:
            if self.dx - frictionPerFrame < 0.0:
                self.dx == 0.0
            else:
                self.pushX(frictionPerFrame * -1.0)
        elif self.dx < 0.0:
            if self.dx + frictionPerFrame > 0.0:
                self.dx == 0.0
            else:
                self.pushX(frictionPerFrame)

    #--------------------------------------------------------------------------
    #      Method: applyGravity
    #
    # Description: Applies downward acceleration (up to a maximum rate) unless
    #              the character is flying or climbing.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def applyGravity(self):
        if not self.isClimbing and not self.isFlying:
            self.pushY(GRAVITY_PER_FRAME)

    #--------------------------------------------------------------------------
    #      Method: jump
    #
    # Description: Applies the maximum rate of upward acceleration if the
    #              character's feet are currently on the ground.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def jump(self):
        if self.onGround():
            self.pushY(self.maxSpeedY * -2.0) # Doubled to ensure max accel.

    #--------------------------------------------------------------------------
    #      Method: move
    #
    # Description: Changes the character's position according to its velocity
    #              along the x- and y-axes, except where collision occurs along
    #              a given axis. Also adjusts the character's stance (e.g.,
    #              foot up or down) as appropriate.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def move(self):
        # Get horizontal movement values.
        absX = self.roundUp(abs(self.dx))
        signX = 1
        if self.dx < 0.0:
            signX = -1

        # Get vertical movement values.
        absY = self.roundUp(abs(self.dy))
        signY = 1
        if self.dy < 0.0:
            signY = -1

        # Perform horizontal movement.
        pixelsMoved = 0
        for x in range(absX):
            if self.isColliding(self.x + (1 * signX), self.y):
                self.dx == 0.0
                break
            else:
                self.x += (1 * signX)
                pixelsMoved += 1

        # Perform vertical movement.
        for y in range(absY):
            if self.isColliding(self.x, self.y + (1 * signY)):
                self.dy == 0.0
                break
            else:
                self.y += (1 * signY)

        # Adjust the character's stance as appropriate.
        self.moveCount += pixelsMoved
        self.moveCount = self.moveCount % (DEFAULT_PIXELS_PER_STANCE_CHANGE *
                                           2)
        if self.moveCount >= 0 and \
           self.moveCount < DEFAULT_PIXELS_PER_STANCE_CHANGE:
            self.currentStance += 1
            if self.currentStance >= self.stances:
                self.currentStance = self.stances - 1
        elif self.moveCount >= DEFAULT_PIXELS_PER_STANCE_CHANGE and \
           self.moveCount < (DEFAULT_PIXELS_PER_STANCE_CHANGE * 2):
            self.currentStance -= 1
            if self.currentStance < 0:
                self.currentStance = 1
        if self.dx == 0.0:      # Character is not moving horizontally.
            self.currentStance = 0
            self.moveCount = 0
        if not self.onGround(): # Character is in the air.
            if self.ID == PLAYER:
                self.currentStance = PLAYER_JUMPING_STANCE
                self.moveCount = 0
            elif self.ID == NINJI:
                self.currentStance = 1

    #--------------------------------------------------------------------------
    #      Method: isColliding
    #
    # Description: For a given set of pixel coordinates representing the upper-
    #              left corner of the character, checks for overlap with a
    #              solid tile along any of the character's sides (compensating
    #              for the character's actual width and height) as well as
    #              contact, from above, with the top of a "top-solid" tile.
    #
    #      Inputs: x - Character tile's hypothetical leftmost pixel column.
    #              y - Character tile's hypothetical topmost pixel row.
    #
    #     Outputs: Returns 'True' if the character would collide with a solid
    #              edge at the given coordinates, otherwise 'False'.
    #--------------------------------------------------------------------------
    def isColliding(self, x, y):
        left   = x + self.widthOffset
        right  = x + (CHARACTER_TILE_SIZE - 1) - self.widthOffset
        top    = y + self.heightOffset
        bottom = y + (CHARACTER_TILE_SIZE - 1)
        midX   = x + CHARACTER_TILE_SIZE / 2
        midY   = y + CHARACTER_TILE_SIZE / 2

        # Check for collision with a tile that is completely solid:
        if self.map.isSolidAt(left, top)     or \
           self.map.isSolidAt(right, top)    or \
           self.map.isSolidAt(left, bottom)  or \
           self.map.isSolidAt(right, bottom) or \
           self.map.isSolidAt(left, midY)    or \
           self.map.isSolidAt(right, midY)   or \
           self.map.isSolidAt(midX, top)     or \
           self.map.isSolidAt(midX, bottom):
            return True

        # Check for collision -- from above only -- with a "top-solid" tile:
        elif self.dy >= 0 and \
             (self.map.getTileNumberAt(left, bottom) in TOP_SOLID_TILES or \
              self.map.getTileNumberAt(right, bottom) in TOP_SOLID_TILES):
            return True

        # No collision has been detected.
        return False

    #--------------------------------------------------------------------------
    #      Method: isOverlapping
    #
    # Description: Determines whether this character is colliding with (i.e.,
    #              overlapping) another given game character.
    #
    #      Inputs: other - The other game character to be tested for
    #                      collisions.
    #
    #     Outputs: Returns 'True' if the two characters are overlapping,
    #              otherwise 'False'.
    #--------------------------------------------------------------------------
    def isOverlapping(self, other):
        selfLeft   = self.x + self.widthOffset
        selfRight  = self.x + (CHARACTER_TILE_SIZE - 1) - self.widthOffset
        selfTop    = self.y + self.heightOffset
        selfBottom = self.y + (CHARACTER_TILE_SIZE - 1)

        otherLeft   = other.x + other.widthOffset
        otherRight  = other.x + (CHARACTER_TILE_SIZE - 1) - other.widthOffset
        otherTop    = other.y + other.heightOffset
        otherBottom = other.y + (CHARACTER_TILE_SIZE - 1)

        return selfRight >= otherLeft and selfLeft <= otherRight and \
               selfTop <= otherBottom and selfBottom >= otherTop

    #--------------------------------------------------------------------------
    #      Method: willFall
    #
    # Description: Determines whether the character is about to fall off a
    #              ledge.
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if the character's feet are on a solid surface next
    #              to a ledge, 'False' otherwise.
    #--------------------------------------------------------------------------
    def willFall(self):
        left   = self.x
        right  = self.x + CHARACTER_TILE_SIZE + 1# - self.widthOffset
        bottom = self.y + CHARACTER_TILE_SIZE + 1
##        return self.onGround() and ((self.facingRight and not \
##                                     self.isColliding(right, bottom)) or \
##                                    (not self.facingRight and not \
##                                     self.isColliding(left, bottom)))
        return self.onGround() and ((self.facingRight and \
                                     self.map.isNonSolidAt(right, bottom)) or \
                                    (not self.facingRight and \
                                     self.map.isNonSolidAt(left, bottom)))

    #--------------------------------------------------------------------------
    #      Method: onGround
    #
    # Description: Determines whether the character's feet are touching a solid
    #              tile.
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if the character's feet are directly above a solid
    #              or top-solid tile, 'False' otherwise.
    #--------------------------------------------------------------------------
    def onGround(self):
        return self.isColliding(self.x, self.y + 1)

    #--------------------------------------------------------------------------
    #      Method: onIce
    #
    # Description: Determines whether the character's feet are on an icy tile.
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if the character's feet are directly above an icy
    #              tile, 'False' otherwise.
    #--------------------------------------------------------------------------
    def onIce(self):
        return self.getTileNumberBelow() in ICY_TILES

    #--------------------------------------------------------------------------
    #      Method: getTileNumberBehind
    #
    # Description: Returns the tile number corresponding to the map tile
    #              directly behind the character (behind the center of the
    #              character's feet, to be more specific).
    #
    #      Inputs: None.
    #
    #     Outputs: The tile number of the map tile behind the character.
    #--------------------------------------------------------------------------
    def getTileNumberBehind(self):
        return self.map.getTileNumberAt(self.x + CHARACTER_TILE_SIZE / 2,
                                        self.y + CHARACTER_TILE_SIZE - 1)

    #--------------------------------------------------------------------------
    #      Method: getTileNumberBelow
    #
    # Description: Returns the tile number corresponding to the map tile
    #              directly below the character (i.e., one pixel lower than the
    #              character's lowest pixel at its midpoint).
    #
    #      Inputs: None.
    #
    #     Outputs: The tile number of the map tile underneath the character.
    #--------------------------------------------------------------------------
    def getTileNumberBelow(self):
        return self.map.getTileNumberAt(self.x + CHARACTER_TILE_SIZE / 2,
                                        self.y + CHARACTER_TILE_SIZE + 1)

    #--------------------------------------------------------------------------
    #      Method: roundUp
    #
    # Description: Given a floating point value, returns the nearest integer
    #              value -- in intervals of MINIMUM_PIXELS_PER_FRAME -- that is
    #              greater than or equal to the floating point value.
    #
    #      Inputs: n - Floating point value to be rounded up.
    #
    #     Outputs: The rounded up value: the lowest integer greater than or
    #              equal to 'n' that is divisible by the minimum number of
    #              pixels to move each frame.
    #--------------------------------------------------------------------------
    def roundUp(self, n):
        minimum = MINIMUM_PIXELS_PER_FRAME
        return ((int(math.ceil(n)) + (minimum - 1)) / minimum) * minimum

#------------------------------------------------------------------------------
#       Class: PlayerCharacter
#
# Description: Represents the player character.
#------------------------------------------------------------------------------
class PlayerCharacter(GameCharacter):
    #--------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Initializes the player character's basic stats.
    #
    #      Inputs: tiles  - The game character tileset.
    #              map    - The current map/level.
    #              screen - The screen on which the game is displayed.
    #              x      - Initial x-coordinate for the player character
    #                       tile's upper-left pixel.
    #              y      - Initial y-coordinate for the player character
    #                       tile's upper-left pixel.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def __init__(self, tiles, map, screen, x, y):
        GameCharacter.__init__(self,
                               PLAYER,
                               PLAYER_MAX_SPEED_X,
                               PLAYER_MAX_SPEED_Y,
                               PLAYER_ACCELERATION_RATE,
                               tiles,
                               FIRST_PLAYER_TILE_BIG,
                               PLAYER_STANCES,
                               PLAYER_WIDTH_OFFSET,
                               PLAYER_HEIGHT_OFFSET_BIG,
                               map,
                               screen,
                               x,
                               y)
        self.invincibilityTimer = 0

    #--------------------------------------------------------------------------
    #      Method: gameLogic
    #
    # Description: Determines the player character's behavior according to
    #              keyboard input and interactions among all active game
    #              objects.
    #
    #      Inputs: keys    - Keys that are currently pressed down.
    #              newKeys - Keys that have just begun to be pressed down.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def gameLogic(self, keys, newKeys):
        # Check for damage and death:
        if self.getTileNumberBelow() == SPIKE_TILE:
            self.takeDamage()
        elif self.y + self.heightOffset > (self.map.mapHeight * MAP_TILE_SIZE):
            self.die()

        # Check invincibility timer:
        if self.invincibilityTimer > 0:
            self.invincibilityTimer -= 1

        # Check crouching/climbing status:
        if self.isCrouching and pygame.K_DOWN not in keys and \
           pygame.K_s not in keys:
            self.stand()
        if self.isClimbing:
            if not self.canClimb():
                self.isClimbing = False
            else:
                self.dy = 0.0

        # Horizontal acceleration:
        self.applyFriction()
        if pygame.K_LEFT in keys or pygame.K_a in keys:
            self.left()
        if pygame.K_RIGHT in keys or pygame.K_d in keys:
            self.right()

        # Vertical acceleration:
        self.applyGravity()
        if pygame.K_SPACE in newKeys:
            self.jump()

        # Climbing:
        if (pygame.K_UP in keys or pygame.K_w in keys) and \
           self.canClimb():
            self.climbUp()
        elif (pygame.K_DOWN in keys or pygame.K_s in keys) and \
           self.canClimb():
            self.climbDown()

        # Crouching:
        if (pygame.K_DOWN in keys or pygame.K_s in keys) and not \
           self.isClimbing:
            self.crouch()

        # Apply motion:
        self.move()

    #--------------------------------------------------------------------------
    #      Method: draw
    #
    # Description: Draws the player character on the screen.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def draw(self):
        # If invincible, the player is sometimes not drawn for flicker effect:
        if self.isInvincible() and random.randint(0, 1):
            return

        position = ((SCREEN_SIZE_X - 1) / 2 * MAP_TILE_SIZE,
                    (SCREEN_SIZE_Y - 1) / 2 * MAP_TILE_SIZE)

        # Crouching:
        if self.isCrouching:
            if self.isBig():
                self.screen.blit(self.tiles.getTile(CROUCHING_TILE_BIG),
                                 position)
            else:
                self.screen.blit(self.tiles.getTile(CROUCHING_TILE_SMALL),
                                 position)

        # Climbing:
        elif self.isClimbing:
            if self.isBig():
                self.screen.blit(self.tiles.getTile(
                    FIRST_CLIMBING_TILE_BIG + self.moveCount % 2),
                                 position)
            else:
                self.screen.blit(self.tiles.getTile(
                    FIRST_CLIMBING_TILE_SMALL + self.moveCount % 2),
                                 position)

        # Facing right:
        elif self.facingRight:
            self.screen.blit(self.tiles.getTile(self.firstTile +
                                                self.currentStance),
                             position)

        # Facing left:
        else:
            self.screen.blit(self.tiles.getTile(self.firstTile + self.stances +
                                                self.currentStance),
                             position)

    #--------------------------------------------------------------------------
    #      Method: isBig
    #
    # Description: Determines whether the player character is big (i.e., in
    #              full health).
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if the character is big, 'False' otherwise.
    #--------------------------------------------------------------------------
    def isBig(self):
        return self.firstTile == FIRST_PLAYER_TILE_BIG

    #--------------------------------------------------------------------------
    #      Method: isSmall
    #
    # Description: Determines whether the player character is small (i.e., has
    #              taken damage).
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if the character is small, 'False' otherwise.
    #--------------------------------------------------------------------------
    def isSmall(self):
        return self.firstTile == FIRST_PLAYER_TILE_SMALL

    #--------------------------------------------------------------------------
    #      Method: grow
    #
    # Description: Makes the player character big (i.e., restores full health).
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def grow(self):
        self.firstTile = FIRST_PLAYER_TILE_BIG
        self.heightOffset = PLAYER_HEIGHT_OFFSET_BIG

    #--------------------------------------------------------------------------
    #      Method: shrink
    #
    # Description: Makes the player character small (i.e., if any more damage
    #              is taken, the player character will die).
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def shrink(self):
        self.firstTile = FIRST_PLAYER_TILE_SMALL
        self.heightOffset = PLAYER_HEIGHT_OFFSET_SMALL

    #--------------------------------------------------------------------------
    #      Method: isInvincible
    #
    # Description: Determines whether the player is currently invincible.
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if the character is invincible, 'False' otherwise.
    #--------------------------------------------------------------------------
    def isInvincible(self):
        return self.invincibilityTimer > 0

    #--------------------------------------------------------------------------
    #      Method: crouch
    #
    # Description: Causes the player character to crouch.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def crouch(self):
        self.isCrouching = True

    #--------------------------------------------------------------------------
    #      Method: stand
    #
    # Description: Causes the player character to stand (i.e., cease crouching).
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def stand(self):
        self.isCrouching = False

    #--------------------------------------------------------------------------
    #      Method: startClimbing
    #
    # Description: Initiates the player character's climbing behavior.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def startClimbing(self):
        self.isClimbing = True
        self.dx = 0.0
        self.dy = 0.0

    #--------------------------------------------------------------------------
    #      Method: climb
    #
    # Description: Causes Toad to move in a given vertical direction according
    #              to his climbing rate.
    #
    #      Inputs: direction - The direction in which to climb: a positive
    #                          value for upward movement, negative for downward
    #                          movement.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def climb(self, direction):
        if not self.isClimbing:
            self.startClimbing()
        self.dy = PLAYER_CLIMBING_RATE * direction

    #--------------------------------------------------------------------------
    #      Method: climbUp
    #
    # Description: Causes Toad to climb upwards.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def climbUp(self):
        self.climb(-1)

    #--------------------------------------------------------------------------
    #      Method: climbDown
    #
    # Description: Causes Toad to climb downwards.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def climbDown(self):
        self.climb(1)

    #--------------------------------------------------------------------------
    #      Method: canClimb
    #
    # Description: Determines whether Toad can climb based on the tile directly
    #              behind him.
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if Toad can climb, 'False' otherwise.
    #--------------------------------------------------------------------------
    def canClimb(self):
        return self.getTileNumberBehind() in CLIMBABLE_TILES

    #--------------------------------------------------------------------------
    #      Method: takeDamage
    #
    # Description: Causes Toad to take damage. If Toad was big, he is now small
    #              and temporarily invincible. If Toad was already small, he is
    #              now dead.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def takeDamage(self):
        if not self.isInvincible():
            if self.isSmall():
                self.die()
            else:
                self.shrink()
                self.invincibilityTimer = INVINCIBILITY_AFTER_DAMAGE

    #--------------------------------------------------------------------------
    #      Method: poseAndPause
    #
    # Description: Displays the player character in a given pose for a given
    #              number of seconds (during which everything will be paused).
    #
    #      Inputs: pose  - Tile number of the desired pose.
    #              pause - Duration of the pause, measured in seconds.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def poseAndPause(self, pose, pause):
        # Draw the map again to erase the player's previous tile:
        x = self.x - ((SCREEN_SIZE_X / 2) * MAP_TILE_SIZE)
        y = self.y - ((SCREEN_SIZE_Y / 2) * MAP_TILE_SIZE)
        self.map.draw(x, y)

        # Draw the desired pose, then pause the game:
        position = ((SCREEN_SIZE_X - 1) / 2 * MAP_TILE_SIZE,
                    (SCREEN_SIZE_Y - 1) / 2 * MAP_TILE_SIZE)
        self.screen.blit(self.tiles.getTile(pose), position)
        pygame.display.flip()
        time.sleep(pause)

    def die(self):
        self.poseAndPause(PLAYER_DEAD_TILE, 1)
        self.grow()
        self.facingRight   = True
        (self.x, self.y)   = self.map.playerStartingPosition
        (self.dx, self.dy) = (0, 0)

    def victoryPose(self):
        if self.isBig():
            pose = PLAYER_VICTORY_TILE_BIG       # Big, facing forward.
        elif self.facingRight:
            pose = PLAYER_VICTORY_TILE_SMALL     # Small, facing right.
        else:
            pose = PLAYER_VICTORY_TILE_SMALL + 1 # Small, facing left.
        self.poseAndPause(pose, 1)

#------------------------------------------------------------------------------
#       Class: NonPlayerCharacter
#
# Description: Represents an NPC.
#
#     Methods: __init__, gameLogic, draw
#------------------------------------------------------------------------------
class NonPlayerCharacter(GameCharacter):
    def __init__(self, ID, tiles, map, screen, x, y, facingRight=False):
        maxSpeedX        = DEFAULT_NPC_MAX_SPEED_X
        maxSpeedY        = DEFAULT_NPC_MAX_SPEED_Y
        accelerationRate = DEFAULT_NPC_ACCELERATION_RATE
        widthOffset      = DEFAULT_WIDTH_OFFSET
        heightOffset     = DEFAULT_HEIGHT_OFFSET
        firstTile        = NPC_FIRST_TILES[ID]
        stances          = DEFAULT_STANCES

        if ID == SPARK:
            stances = SPARK_STANCES
        elif ID == ALBATOSS:
            stances = ALBATOSS_STANCES
        elif ID == PHANTO:
            stances = PHANTO_STANCES

        GameCharacter.__init__(self,
                               ID,
                               maxSpeedX,
                               maxSpeedY,
                               accelerationRate,
                               tiles,
                               firstTile,
                               stances,
                               widthOffset,
                               heightOffset,
                               map,
                               screen,
                               x,
                               y,
                               facingRight)

        if ID == SPARK or ID == ALBATOSS or ID == PHANTO:
            self.isFlying = True

    #--------------------------------------------------------------------------
    #      Method: gameLogic
    #
    # Description: Determines the NPC's behavior according to interactions
    #              among all active game objects.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def gameLogic(self):
        # Check for a change in orientation:
        if (self.facingRight and self.isColliding(self.x +                    \
                                                  CHARACTER_TILE_SIZE -       \
                                                  self.widthOffset * 3,       \
                                                  self.y))                 or \
           (not self.facingRight and self.isColliding(self.x - 1, self.y)) or \
           (self.isFlying and ((not self.facingRight and self.x - 1 <= 0)  or \
                               (self.facingRight and self.x + \
                                CHARACTER_TILE_SIZE -         \
                                self.widthOffset * 2 >=       \
                                self.map.getSize()[0] * MAP_TILE_SIZE)))   or \
           (self.ID == SHY_GUY_BLUE and self.willFall()):
            self.facingRight = not self.facingRight
            self.dx *= -1.0

        # Horizontal acceleration:
        self.applyFriction()
        if self.facingRight:
            self.right()
        else:
            self.left()

        # Vertical acceleration:
        self.applyGravity()
        if self.ID == NINJI:
            self.jump()

        # Apply motion:
        self.move()

    #--------------------------------------------------------------------------
    #      Method: draw
    #
    # Description: Draws the NPC on the screen, if currently visible.
    #
    #      Inputs: mapX - Left-most map pixel currently being displayed.
    #              mapY - Top-most map pixel currently being displayed.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def draw(self, mapX, mapY):
        if self.x < mapX or self.x > (mapX + SCREEN_SIZE_X *
                                      MAP_TILE_SIZE) or \
           self.y < mapY or self.y > (mapY + SCREEN_SIZE_Y * MAP_TILE_SIZE):
            return
        position = (self.x - mapX - MAP_TILE_SIZE,
                    self.y - mapY - MAP_TILE_SIZE)
        if self.facingRight:
            self.screen.blit(self.tiles.getTile(self.firstTile +
                                                self.currentStance), position)
        else:
            self.screen.blit(self.tiles.getTile(self.firstTile + self.stances +
                                                self.currentStance), position)
