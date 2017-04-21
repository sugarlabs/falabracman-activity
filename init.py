# -*- coding: iso-8859-1 -*-
#Copyright (C) 2008 by Achuras Experience
#
#This file is part of Falabracman
#
#Falabracman is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#The Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#Falabracman is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with Falabracman.  If not, see <http://www.gnu.org/licenses/>.


from config import * 
import pygame
from pygame.locals import *
import gettext

#Inicializamos pygame y sonido
pygame.mixer.pre_init(44100, -16, False)
pygame.init()

# Definimos la pantalla
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Titulo
pygame.display.set_caption("falabracman")

#Inicializacion del gettext
#gettext.bindtextdomain('falabracman', '/usr/share/locale')
#gettext.textdomain('falabracman')


