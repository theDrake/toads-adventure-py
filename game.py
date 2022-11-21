#-------------------------------------------------------------------------------
#    Filename: game.py
#
#      Author: David C. Drake (https://davidcdrake.com)
#
# Description: Contains an abstract 'Game' class.
#-------------------------------------------------------------------------------

import pygame
from pygame import display, time, event

#-------------------------------------------------------------------------------
#       Class: Game
#
# Description: An abstract class for fullscreen games.
#
#     Methods: __init__, game_logic (virtual), paint (virtual), main_loop
#-------------------------------------------------------------------------------
class Game:
    #---------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Initializes the game's display mode and basic stats.
    #
    #      Inputs: fps - Desired frames per second.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def __init__(self, fps=60):
        self.fps = fps
        self.screen = display.set_mode((0, 0), pygame.FULLSCREEN |
                                       pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.width = display.Info().current_w
        self.height = display.Info().current_h
        self.on = True

    #---------------------------------------------------------------------------
    #      Method: game_logic
    #
    # Description: Virtual method intended to perform underlying game logic
    #              according to player input.
    #
    #      Inputs: keys     - Keys currently pressed.
    #              new_keys - Keys currently pressed that weren't before.
    #
    #     Outputs: Raises an error if not implemented by a child class.
    #---------------------------------------------------------------------------
    def game_logic(self, keys, new_keys):
        raise NotImplementedError()

    #---------------------------------------------------------------------------
    #      Method: paint
    #
    # Description: Virtual method intended to draw images to the screen.
    #
    #      Inputs: surface - The surface on which to draw.
    #
    #     Outputs: Raises an error if not implemented by a child class.
    #---------------------------------------------------------------------------
    def paint(self, surface):
        raise NotImplementedError()

    #---------------------------------------------------------------------------
    #      Method: main_loop
    #
    # Description: Manages game speed, 'QUIT' events, and keyboard input. Calls
    #              'game_logic' and 'draw', then updates the display.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def main_loop(self):
        clock = time.Clock()
        keys = set()
        while True:
            clock.tick(self.fps)
            new_keys = set()
            for e in event.get():
                if (e.type == pygame.QUIT or
                    (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE)):
                    pygame.quit()
                    return
                if e.type == pygame.KEYDOWN:
                    keys.add(e.key)
                    new_keys.add(e.key)
                if e.type == pygame.KEYUP:
                    keys.discard(e.key)
            if self.on:
                self.game_logic(keys, new_keys)
                self.paint(self.screen)
                display.flip()
