from gettext import gettext as _


import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import pygame
import sugargame
from sugargame.canvas import PygameCanvas
from sugar3.activity.activity import Activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.activity.widgets import StopButton


sys.path.append('..')  # Import sugargame package from top directory.
import sugargame.canvas

import TestGame

class activity(Activity):

    def __init__(self, handle):
        Activity.__init__(self, handle)
        
        self.paused = False
        
        # Create the game instances
        self.game = TestGame
        self.game.canvas = sugargame.canvas.PygameCanvas(
                self,
                main=self.game.main,
                modules=[pygame.display, pygame.font])
        self.set_canvas(self.game.canvas)
        self.game.canvas.grab_focus()
        # Build the activity toolbar.
        self.build_toolbar()

        # Build the Pygame canvas and start the game running
        # (self.game.run is called when the activity constructor
        # returns).
        
        # Note that set_canvas implicitly calls read_file when
        # resuming from the Journal.


    def build_toolbar(self):
        toolbar_box = ToolbarBox()
        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, -1)
        activity_button.show()





        
        
