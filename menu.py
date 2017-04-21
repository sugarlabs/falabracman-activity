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


import pygame
from pygame.locals import *
from olpcgames import pausescreen
from init import screen
import gettext 
import locale 
import os
import config

gettext.bindtextdomain('falabracman', 'data/locales')
gettext.textdomain('falabracman')

clock = pygame.time.Clock()
imagen_presentacion = pygame.image.load("images/splash.jpg").convert()
imagen_creditos = pygame.image.load("images/creditos.jpg").convert()
sonido_menu = pygame.mixer.Sound("sounds/menu.ogg")

def mostrarImagen(imagen, duracion):
    screen.blit(imagen, imagen.get_rect(center=screen.get_rect().center))
    ticks_final = pygame.time.get_ticks() + duracion * 1000

    while pygame.time.get_ticks() < ticks_final:
        for e in pausescreen.get_events(config.DEMORA_PAUSA):
            if e.type == KEYDOWN:
                if e.key in [K_ESCAPE, K_SPACE, K_RETURN]:
                    sonido_menu.play()
                    return
        pygame.display.flip()
        clock.tick(10)

class Menu:
    font = pygame.font.Font('fonts/ds_moster.ttf', 48)
    fondo = pygame.image.load("images/menu.jpg").convert()
    colorEncendido = (200,0,0)
    colorApagado = (0,0,0)
    seleccionado = 0

    def __init__(self, opciones):
        self.opciones = opciones
        self.actualizar()

    def actualizar(self):
        self.imagenes = []
        for texto, funcion in self.opciones:
            texto_traducido = gettext.gettext(texto)
            print texto, gettext.gettext(texto)
            imagen0 = self.font.render(texto_traducido, 1, self.colorApagado)
            imagen1 = self.font.render(texto_traducido, 1, self.colorEncendido)
            self.imagenes.append( [imagen0, imagen1] )
        self.dibujarFondo()
        self.dibujarOpciones()

    def dibujarOpciones(self):
        altura_de_opcion = 60
        x = 405
        y = 405
        
        for indice, imagenes in enumerate(self.imagenes):
            posicion = (x, y + altura_de_opcion * indice)
            area = imagenes[0].get_rect(topleft=posicion)
            screen.blit(self.fondo, posicion, area)

        for indice, imagenes in enumerate(self.imagenes):
            if indice == self.seleccionado:
                imagen = imagenes[1]
            else:
                imagen = imagenes[0]
            posicion = (x, y + altura_de_opcion * indice)
            screen.blit(imagen, posicion)
        pygame.display.flip()

    def moverSeleccion(self, direccion):
        self.seleccionado += direccion
        # procura que el cursor esté entre las opciones permitidas
        if self.seleccionado < 0:
            self.seleccionado = 0
        elif self.seleccionado > len(self.opciones) - 1:
            self.seleccionado = len(self.opciones) - 1
        sonido_menu.play() 
        self.dibujarOpciones()

    def dibujarFondo(self):
        screen.blit(self.fondo, (0, 0))

    def salirDelMenu(self):
        self.salir = True

    def run(self):
        self.salir = False
        while not self.salir:
            for e in pausescreen.get_events(config.DEMORA_PAUSA):
                if e.type == QUIT:
                    salir = True
                if e.type == KEYDOWN:
                    if e.key in [K_UP, K_KP8]:
                        self.moverSeleccion(-1)
                    elif e.key in [K_DOWN, K_KP2]:
                        self.moverSeleccion(1)
                    elif e.key in [K_RETURN, K_KP7, K_KP1, K_KP3, K_KP9]:
                        sonido_menu.play() 
                        titulo, funcion = self.opciones[self.seleccionado]
                        funcion()
                        self.actualizar()
                        break
            pygame.display.flip()
            clock.tick(10)

class MenuIdiomas(Menu):
    def __init__(self):
        opciones = [
            ("portuguese", self.cambiar_locale_bra),
            ("spanish", self.cambiar_locale_esp),
            ("return", self.salirDelMenu),
        ]
        Menu.__init__(self, opciones)

    def cambiar_locale_bra(self):
        #Deprecated
        self.lang = "bra"
        os.environ["LANG"]="pt_BR"

    def cambiar_locale_esp(self):
        #Deprecated
        self.lang = "esp"
        os.environ["LANG"]="es_AR"
        locale.setlocale(locale.LC_ALL, "es_AR.UTF-8")

class MenuPrincipal(Menu):
    def __init__(self):
        opciones = [
            ("play", self.comenzar_nuevo_juego),
            ("options", self.mostrar_opciones),
            ("credits", self.mostrar_creditos),
            ("quit", self.salirDelMenu)
        ]
        Menu.__init__(self, opciones)

    def comenzar_nuevo_juego(self):
        systemLang=os.environ["LANG"][:2]
        if systemLang=="es":
            print "Cambiando el lenguaje a esp"
            lang = "esp"
        else:
            print "Cambiando el lenguaje a bra"
            lang = "bra"

        import game
        game.main(lang)
 
    def mostrar_opciones(self):
        MenuIdiomas().run()

    def mostrar_creditos(self):
        mostrarImagen(imagen_presentacion, 4)
        mostrarImagen(imagen_creditos, 20)

    def salir_del_programa(self):
        import sys
        print "Gracias por utilizar este programa."
        sys.exit(0)

def main():    
    pygame.mouse.set_visible(False)
    sonido_menu.play()
    mostrarImagen(imagen_presentacion, 3)
    # cargar el resto de las imagenes y sonidos mientras se muestra la pantalla inicial
    import game
    mostrarImagen(imagen_presentacion, 2)
    MenuPrincipal().run()

if __name__ == '__main__':
    pygame.mixer.init()
    main()
