import falabracman
import sugargame.canvas
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.activity import Activity
from sugar3.graphics.style import GRID_CELL_SIZE
import pygame
from gettext import gettext as _

import sys
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

sys.path.append('..')  # Import sugargame package from top directory.


class Falabracman(Activity):

    def __init__(self, handle):
        Activity.__init__(self, handle)

        self.paused = False

        # Create the game instance.
        self.game = falabracman.FalabracmanGame()

        # Build the activity toolbar.
        self.build_toolbar()

        # Build the Pygame canvas and start the game running
        # (self.game.run is called when the activity constructor
        # returns).
        self._pygamecanvas = sugargame.canvas.PygameCanvas(
            self, main=self.game.run, modules=[pygame.display])

        # Note that set_canvas implicitly calls read_file when
        # resuming from the Journal.
        w = Gdk.Screen.width()
        h = Gdk.Screen.height() - GRID_CELL_SIZE

        self._pygamecanvas.set_size_request(w, h)
        self.set_canvas(self._pygamecanvas)
        self._pygamecanvas.grab_focus()

    def build_toolbar(self):
        toolbar_box = ToolbarBox()
        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, -1)
        activity_button.show()

        # Blank space (separator) and Stop button at the end:

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()
        stop_button.connect('clicked', self._stop_cb)

    def _stop_cb(self, arg=None):
        sys.exit()

    def read_file(self, file_path):
        raise NotImplementedError

    def write_file(self, file_path):
        raise NotImplementedError

    def get_preview(self):
        return self._pygamecanvas.get_preview()
