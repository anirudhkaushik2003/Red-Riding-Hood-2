import sys
import os

# When running as a PyInstaller bundle, change to the bundle's directory
# so all relative paths (img/, music/, fonts) resolve correctly
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

from game import Game

if __name__ == "__main__":
    game = Game()
    game.run()
