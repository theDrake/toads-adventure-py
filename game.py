#!/usr/bin/env python

#------------------------------------------------------------------------------
#    Filename: game.py
#
#      Author: David C. Drake (http://davidcdrake.com)
#
# Description: Contains an abstract 'Game' class for windowed games. Developed
#              using Python 2.7.2.
#------------------------------------------------------------------------------

import pygame
import pygame.locals

#------------------------------------------------------------------------------
#       Class: Game
#
# Description: An abstract class for windowed games.
#
#     Methods: __init__, gameLogic (virtual), paint (virtual), mainLoop
#------------------------------------------------------------------------------
class Game:
    #--------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Initializes a windowed game's basic stats. For the display,
    #              double-buffering is used for smooth animation and alpha
    #              blending is applied.
    #
    #      Inputs: name   - Title displayed along the top of the window.
    #              width  - Window width, in pixels.
    #              height - Window height, in pixels.
    #              fps    - Frames per second.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def __init__(self, name, width, height, fps):
        self.width  = width
        self.height = height
        self.fps    = fps
        self.on     = True
        self.screen = pygame.display.set_mode((width, height),
                                              pygame.locals.DOUBLEBUF |
                                              pygame.locals.SRCALPHA)
        pygame.display.set_caption(name)

    #--------------------------------------------------------------------------
    #      Method: gameLogic
    #
    # Description: Virtual method intended to perform underlying game logic
    #              according to player input.
    #
    #      Inputs: keys    - Keys currently pressed.
    #              newKeys - Keys currently pressed that weren't before.
    #
    #     Outputs: Raises an error if not implemented by a child class.
    #--------------------------------------------------------------------------
    def gameLogic(self, keys, newKeys):
        raise NotImplementedError()

    #--------------------------------------------------------------------------
    #      Method: paint
    #
    # Description: Virtual method intended to draw images to the screen.
    #
    #      Inputs: surface - The surface on which to draw.
    #
    #     Outputs: Raises an error if not implemented by a child class.
    #--------------------------------------------------------------------------
    def paint(self, surface):
        raise NotImplementedError()

    #--------------------------------------------------------------------------
    #      Method: mainLoop
    #
    # Description: The game's main loop. Manages game speed, 'QUIT' events,
    #              and keyboard input (if the escape key has been pressed, this
    #              will be treated as a 'QUIT' event). Calls the 'gameLogic'
    #              and 'draw' methods, then updates the display.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def mainLoop(self):
        clock = pygame.time.Clock()
        keys = set()
        while True:
            clock.tick(self.fps)
            newKeys = set()
            for e in pygame.event.get():
                if e.type == pygame.QUIT or \
                   (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                    pygame.quit()
                    return
                if e.type == pygame.KEYDOWN:
                    keys.add(e.key)
                    newKeys.add(e.key)
                if e.type == pygame.KEYUP:
                    keys.discard(e.key)
            if self.on:
                self.gameLogic(keys, newKeys)
                self.paint(self.screen)
            pygame.display.flip()
