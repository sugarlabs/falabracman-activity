# -*- coding: utf-8 -*-
# Copyright (C) 2008 by Achuras Experience
# Copyright (C) 2019 by Srevin Saju (Python3 + Sugargame)

# This file is part of Falabracman
#
# Falabracman is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# The Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Falabracman is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Falabracman.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk
import pygame
from pygame.locals import *
from random import randrange
import random
import gettext
import hollow
from config import *
import gi
import sys
import os
from gi.repository import Gdk
gi.require_version('Gtk', '3.0')

# CONSTANTS
FBM_SPEED = 15
ALTURA_BARRA = 150

# --------------------------
# DISP
# ----------------------------


class Display:
    def __init__(self, parent, area):
        self.parent = parent
        self.area = area
        self.vidas = 0
        self.setDisplay("")

    def setDisplay(self, palabra):
        self.palabra = palabra
        self.encendidas = 0
        self.draw()

    def setVidas(self, vidas):
        self.vidas = vidas
        self.draw()

    def draw(self):
        self.parent.area_barra.blit(self.parent.barra, (0, 0))
        w = 0
        for n, l in enumerate(self.palabra):
            if n >= self.encendidas:
                imagen = self.parent.dameLetra(self.parent.letrasApagadas, l)
            else:
                imagen = self.parent.dameLetra(self.parent.letrasEncendidas, l)
            self.area.blit(imagen, (w, 0))
            w += imagen.get_rect().width

        w = self.area.get_rect().width
        for n in range(self.vidas):
            self.area.blit(self.parent.imagenVida, (w, 0))
            w -= self.parent.imagenVida.get_rect().width

    def encender(self):
        self.encendidas += 1
        self.draw()


# ================================
# EXCEPTIONS INSTANCE
# ================================
class EndOfGame(Exception):
    pass


class YouWon(EndOfGame):
    def __init__(self, parent):
        self.parent = parent
        self.imagen_ganaste = pygame.transform.scale(pygame.image.load(
            "images/ganaste.png").convert_alpha(),
            (int(0.8*self.parent.screen_width),
                int(0.6*self.parent.screen_height)))

    def accion(self):
        self.parent.aplausos.play()
        self.parent.status.message(self.imagen_ganaste)
        pygame.time.delay(3000)


class YouLost(EndOfGame):
    def __init__(self, parent):
        self.parent = parent
        self.imagen_perdiste = pygame.transform.scale(pygame.image.load(
            "images/perdio.png").convert_alpha(),
            (int(0.8*self.parent.screen_width),
                int(0.6*self.parent.screen_height)))

    def accion(self):
        self.parent.status.message(self.imagen_perdiste)
        pygame.time.delay(3000)


# ================================
# SPRITE INSTANCE
# ================================
class GrossiniSprite(pygame.sprite.Sprite):

    def __init__(self, parent):
        self.parent = parent
        self.SPEED = FBM_SPEED
        self.imagenes = [pygame.transform.scale(pygame.image.load(
            "images/zeek%d.png" % n).convert_alpha(),
            (int(0.08*self.parent.screen_width),
                int(0.12*self.parent.screen_height))) for n in range(12)]

    def init(self):
        self.image = self.imagenes[0]
        self.aplauso = pygame.mixer.Sound("sounds/aplauso.ogg")

        self.ciclosCaminata = dict(
            izquierda=[4, 5, 4, 6],
            derecha=[1, 2, 1, 3],
            arriba=[9, 10, 9, 11],
            abajo=[0, 7, 0, 8],
        )
        self.velocidades = dict(
            izquierda=(-1, 0),
            derecha=(1, 0),
            arriba=(0, -1),
            abajo=(0, 1),
        )
        self.hundido = False
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect(
            topright=self.parent.playing_area.get_rect().topright)
        self.cuadros = self.ciclosCaminata["abajo"]
        self.frenar()

    def frenar(self):
        self.velocidad = (0, 0)
        self.numeroCuadro = 0

    def step(self):
        dx, dy = self.velocidad
        self.image = self.imagenes[self.cuadros[self.numeroCuadro]]
        if dx != 0 or dy != 0:
            self.numeroCuadro = (self.numeroCuadro + 1) % 4
            self.rect.move_ip((dx*self.SPEED, dy*self.SPEED))
            if not self.parent.playing_area.get_rect().contains(self.rect):
                self.rect.clamp_ip(self.parent.playing_area.get_rect())
                self.frenar()

    def mirar(self, direccion):
        self.cuadros = self.ciclosCaminata[direccion]
        self.velocidad = self.velocidades[direccion]
        self.numeroCuadro = 0


# ==================================
# COLLISIONABLE SPRITE
# ==================================
class Collisionable(pygame.sprite.Sprite):
    def __init__(self, parent, otros):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = self.image.get_rect()
        colisiona = True
        contador = 99
        while colisiona and contador > 0:
            self.rect.center = (randrange(self.parent.playing_area.get_rect(
            ).width), randrange(self.parent.playing_area.get_rect().height))
            self.rect.clamp_ip(self.parent.playing_area.get_rect())
            contador -= 1
            colisiona = False
            for g in otros:
                if pygame.sprite.spritecollide(self, g, False):
                    colisiona = True


# ==================================
# LETTER SPRITE
# ==================================
class LetterSprite(Collisionable):
    def __init__(self, parent):
        self.parent = parent
        self.sound = pygame.mixer.Sound("sounds/money.ogg")

    def spritefx(self, grossini, letra):
        self.image = self.parent.dameLetra(self.parent.letrasEncendidas, letra)
        self.letra = letra
        Collisionable.__init__(self, self.parent, grossini)


# ==================================
# LETTER SPRITE SOUND
# ==================================
class LetterSprite_Sound:
    def __init__(self):
        self.sound = pygame.mixer.Sound("sounds/money.ogg")


# ==================================
# IMPACT COLLISION SPRITE
# ==================================
class Lago(Collisionable):
    def __init__(self, parent, otros):
        self.sound = pygame.mixer.Sound("sounds/splash.ogg")

        self.imagenes = [pygame.transform.scale(pygame.image.load(
            "images/lago%d.png" % n).convert_alpha(),
            (int(parent.screen_width*0.15),
             int(parent.screen_height*0.15))) for n in [0, 1, 2, 3]]
        self.image = random.choice(self.imagenes)
        Collisionable.__init__(self, parent, otros)


# ==================================
# IMPACT COLLISION SPRITE SOUND
# ==================================
class Lago_Sound:
    def __init__(self):
        self.sound = pygame.mixer.Sound("sounds/splash.ogg")


# ==================================
# PALABRA SPRITE
# ==================================
class Palabra(pygame.sprite.Group):
    def __init__(self, parent, palabra, groupsinni, lagos):
        self.parent = parent
        pygame.sprite.Group.__init__(self)

        for letra in palabra.strip():
            lettersprite_obj = LetterSprite(self.parent)
            lettersprite_obj.spritefx([groupsinni, lagos, self], letra)
            self.add(lettersprite_obj)

# ==================================
# LAGOS SPRITE
# ==================================


class Lagos(pygame.sprite.Group):
    def __init__(self, parent, numLagos, groupsinni):
        pygame.sprite.Group.__init__(self)
        for n in range(numLagos):
            self.add(Lago(parent, [groupsinni, self]))


# ==================================
# LEVEL OBJECT
# ==================================
class Level:

    def __init__(self, parent, numero, dic, grossini, groupsinni):
        self.parent = parent
        self.base_background = pygame.image.load("images/fondo.jpg").convert()
        self.base_background = pygame.transform.scale(
            self.base_background,
            (self.parent.screen_width, self.parent.screen_height))
        self.background = self.base_background.copy()
        self.finNivel = False
        self.palabras = [dic.getRandomWordByCategory().upper().encode("utf-8")
                         for n in range(numero)]
        self.numero = numero
        self.grupoLagos = Lagos(self.parent, 5, groupsinni)
        self.groupsinni = groupsinni
        self.grupoLagos.draw(self.background)
        self.nuevaPalabra(grossini)
        self.parent.playing_area.blit(self.background, (0, 0))

    def nuevaPalabra(self, grossini):
        self.palabra = self.palabras.pop()
        self.grupoLetras = Palabra(
            self.parent, self.palabra, self.groupsinni, self.grupoLagos)
        self.encontradas = []
        self.parent.display.setDisplay(self.palabra)
        self.parent.playing_area.blit(self.background, (0, 0))

    def draw(self, area):
        self.grupoLetras.clear(area, self.background)
        self.grupoLetras.draw(area)

    def hayMasPalabras(self):
        return len(self.palabras) > 0

    def verificarColisiones(self, grossini):
        charcos_colisionados = pygame.sprite.spritecollide(
            grossini, self.grupoLagos, False)
        letras_colisionadas = pygame.sprite.spritecollide(
            grossini, self.grupoLetras, False)

        if charcos_colisionados:
            sndinst = Lago_Sound()
            sndinst.sound.play()
            grossini.hundido = True

        if letras_colisionadas:
            for l in letras_colisionadas:
                if l.letra == self.palabra[len(self.encontradas)]:
                    self.encontradas.append(l.letra)
                    # grossini.frenar()
                    self.grupoLetras.remove(l)
                    soundinst_LetterSprite = LetterSprite_Sound()
                    soundinst_LetterSprite.sound.play()
                    self.parent.display.encender()
                    if len(self.encontradas) == len(self.palabra):
                        if self.hayMasPalabras():
                            self.nuevaPalabra(grossini)
                        else:
                            self.finNivel = True

# ==================================
# SPRITE STATUS
# ==================================


class Status:
    def __init__(self, parent, dic):
        self.parent = parent
        self.dic = dic
        self.nroNivel = 0
        self.nivelMaximo = 1
        self.setVidas(VIDAS)
        self.groupsinni = None
        self.resetGrossini()
        self.avanzarNivel()

    def resetGrossini(self):
        if self.groupsinni is not None:
            self.groupsinni.clear(
                self.parent.playing_area, self.nivel.background)

        self.grossini = GrossiniSprite(self.parent)
        self.grossini.init()
        # aca karucha
        self.groupsinni = pygame.sprite.Group()
        self.groupsinni.add(self.grossini)

    def avanzarNivel(self):
        self.nroNivel += 1
        self.nivel = Level(self.parent, self.nroNivel,
                           self.dic, self.grossini, self.groupsinni)
        self.parent.aplausos.play()

    def draw(self, area):
        self.groupsinni.clear(area, self.nivel.background)
        self.nivel.draw(area)
        self.groupsinni.draw(area)

    def setVidas(self, vidas):
        self.vidas = vidas
        self.parent.display.setVidas(vidas)

    def message(self, msg):
        clock = pygame.time.Clock()
        self.parent.playing_area.blit(msg, msg.get_rect(
            center=self.parent.playing_area.get_rect().center))
        pygame.display.flip()
        clock.tick(4)

    def step(self):
        self.grossini.step()
        self.nivel.verificarColisiones(self.grossini)
        if self.grossini.hundido:
            self.setVidas(self.vidas-1)
            self.resetGrossini()
        if self.nivel.finNivel:
            if self.nivel.numero > self.nivelMaximo:
                raise YouWon(self.parent)
            self.avanzarNivel()

        if self.vidas == 0:
            raise YouLost(self.parent)


# ==================================
# PYGAME MAIN
# ==================================
class FalabracmanGame:

    def __init__(self):
        self.menu_to_game_loop = True
        self.load_game_bool = True
        pass

    # =============== < MENU > =================
    def continue_to_game(self):
        self.exit = True

    def update_menu(self):
        self.imagenes = []
        for texto, funcion in self.options:
            texto_traducido = gettext.gettext(texto)
            imagen0 = self.font.render(texto_traducido, 1, self.colorApagado)
            imagen1 = self.font.render(texto_traducido, 1, self.colorEncendido)
            self.imagenes.append([imagen0, imagen1])
        self.drawBackground()
        self.drawOptions()
        pygame.display.update()

    def drawOptions(self):
        # FIXME DO NOT HARDCODE COORDINATES
        altura_de_opcion = 60
        x = self.screen_width//4
        y = int(self.screen_height*0.5)

        for indice, imagenes in enumerate(self.imagenes):
            posicion = (x, y + altura_de_opcion * indice)
            area = imagenes[0].get_rect(topleft=posicion)
            self.screen.blit(self.background, posicion, area)

        for indice, imagenes in enumerate(self.imagenes):
            if indice == self.seleccionado:
                imagen = imagenes[1]
            else:
                imagen = imagenes[0]
            posicion = (x, y + altura_de_opcion * indice)
            self.screen.blit(imagen, posicion)
        pygame.display.update()

    def moverSeleccion(self, direccion):
        self.seleccionado += direccion
        # procura que el cursor esté entre las options permitidas
        if self.seleccionado < 0:
            self.seleccionado = 0
        elif self.seleccionado > len(self.options) - 1:
            self.seleccionado = len(self.options) - 1
        self.sonido_menu.play()
        self.drawOptions()

    def drawBackground(self):
        left_padding = (self.screen.get_rect().width-self.screen_width)/2
        self.screen.blit(self.background, (left_padding, 0))

    def exitDelMenu(self):
        self.exit = True
        pygame.quit()
        sys.exit(0)

    def options_menu_init(self):
        self.font = pygame.font.Font('fonts/ds_moster.ttf', 48)
        self.background = pygame.image.load("images/menu.jpg").convert()
        self.background = pygame.transform.scale(self.background,
                                                 (self.screen_width, self.screen_height))
        self.colorEncendido = (200, 0, 0)
        self.colorApagado = (0, 0, 0)
        self.seleccionado = 0
        self.options = [
            ("English", self.set_language_en),
            ("Portugese", self.set_language_bra),
            ("Espanol", self.set_language_esp),
            ("Return", self.return_back_to_menu)
        ]
        self.sonido_menu = pygame.mixer.Sound("sounds/menu.ogg")
        self.update_menu()

    def show_options_menu(self):
        self.options_menu_init()
        self.imagen_presentacion = pygame.image.load(
            "images/splash.jpg").convert()
        self.imagen_presentacion = pygame.transform.scale(self.imagen_presentacion,
                                                          (self.screen_width, self.screen_height))
        self.imagen_creditos = pygame.image.load(
            "images/creditos.jpg").convert()
        self.imagen_creditos = pygame.transform.scale(self.imagen_creditos,
                                                      (self.screen_width, self.screen_height))
        self.menu_run()

    # Set langs in
    def set_language_en(self):
        self.language = 'en'
        self.load_game_bool = False
        pass

    def set_language_bra(self):
        self.language = 'bra'
        os.environ["LANG"] = "pt_BR"
        self.load_game_bool = False
        pass

    def set_language_esp(self):
        self.language = 'esp'
        os.environ["LANG"] = "es_AR"
        self.load_game_bool = False
        pass

    def return_back_to_menu(self):
        self.load_game_bool = False
        pass
    # Set langs out

    def show_credits(self):
        self.show_image(self.imagen_presentacion, 4)
        self.show_image(self.imagen_creditos, 20)
        self.load_game_bool = False

    def menu_init(self):
        self.font = pygame.font.Font('fonts/ds_moster.ttf', 48)
        self.background = pygame.image.load("images/menu.jpg").convert()
        self.background = pygame.transform.scale(self.background,
                                                 (self.screen_width, self.screen_height))
        self.colorEncendido = (200, 0, 0)
        self.colorApagado = (0, 0, 0)
        self.seleccionado = 0
        self.options = [
            ("play", self.continue_to_game),
            ("credits", self.show_credits),
            ("options", self.show_options_menu),
            ("quit", self.exitDelMenu)
        ]
        self.sonido_menu = pygame.mixer.Sound("sounds/menu.ogg")
        self.update_menu()

    def menu_run(self):
        self.update_menu()
        self.exit = False
        while not self.exit:
            while Gtk.events_pending():
                Gtk.main_iteration()

            e = pygame.event.poll()
            if e.type == QUIT:
                self.menu_to_game_loop = False
                self.exit = True
            if e.type == KEYDOWN:
                if e.key in [K_UP, K_KP8]:
                    self.moverSeleccion(-1)
                elif e.key in [K_DOWN, K_KP2]:
                    self.moverSeleccion(1)
                elif e.key in [K_RETURN, K_KP7, K_KP1, K_KP3, K_KP9]:
                    self.sonido_menu.play()
                    titulo, funcion = self.options[self.seleccionado]
                    funcion()
                    self.update_menu()
                    break

            pygame.display.flip()
        pygame.display.update()
        return
    # ============== < MENU > ================

    def dameLetra(self, dictLetras, letra):
        if type(letra) is int:
            return dictLetras.get(chr(letra), dictLetras["*"])
        elif type(letra) is str:
            return dictLetras.get(letra, dictLetras["*"])
        else:
            # FIXME
            raise Exception(
                "A unhandled error has occured. Please report to \n"
                "https://github.com/sugarlabs/falabracman-activity/issues \n"
                "Error: letra: {} \n dictletra : {}".format(letra, dictLetras)
            )

    def armarLetras(self, color1, color2):
        # Arm the player instance
        d = {}
        for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ*":
            d[l] = hollow.textOutline(self.font, l, color1, color2)
        return d

    # Show Image TODO FIXME
    def show_image(self, imagen, duracion):
        self.screen.blit(imagen, imagen.get_rect(
            center=self.screen.get_rect().center))
        ticks_final = pygame.time.get_ticks() + duracion * 1000
        clock = pygame.time.Clock()
        while pygame.time.get_ticks() < ticks_final:

            e = pygame.event.poll()
            if e.type == KEYDOWN:
                if e.key in [K_ESCAPE, K_SPACE, K_RETURN]:
                    self.sonido_menu.play()
                    return
            pygame.display.flip()
            clock.tick(10)

    def call_menu(self):
        self.menu_init()
        self.imagen_presentacion = pygame.image.load(
            "images/splash.jpg").convert()
        self.imagen_presentacion = pygame.transform.scale(self.imagen_presentacion,
                                                          (self.screen_width, self.screen_height))
        self.imagen_creditos = pygame.image.load(
            "images/creditos.jpg").convert()
        self.imagen_creditos = pygame.transform.scale(self.imagen_creditos,
                                                      (self.screen_width, self.screen_height))

        self.menu_run()
        self.sonido_menu.play()

    def game_instance(self):
        import paladict
        dic = paladict.PalaDict(self.language)
        self.status = Status(self, dic)
        # Comienza el juego
        playing = True
        clock = pygame.time.Clock()
        while playing:
            clock.tick(20)

            # Pump GTK Messages
            while Gtk.events_pending():
                Gtk.main_iteration()

            event = pygame.event.poll()
            if event.type == QUIT:
                playing = False
                self.menu_to_game_loop = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    playing = False
                    self.menu_to_game_loop = False
                elif event.key in [K_UP, K_KP8, K_KP9]:
                    self.status.grossini.mirar("arriba")
                elif event.key in [K_DOWN, K_KP2, K_KP3]:
                    self.status.grossini.mirar("abajo")
                elif event.key in [K_LEFT, K_KP4, K_KP7]:
                    self.status.grossini.mirar("izquierda")
                elif event.key in [K_RIGHT, K_KP6, K_KP1]:
                    self.status.grossini.mirar("derecha")
            try:
                self.status.step()
            except EndOfGame as e:
                e.accion()
                break
            pygame.display.update()
            self.status.draw(self.playing_area)

    # Pygame canonical run
    def run(self):
        # Initialize assuming language = en
        self.language = 'en'
        pygame.init()
        pygame.display.flip()
        self.screen = pygame.display.get_surface()
        self.screen_width = self.screen.get_rect().width
        self.screen_height = self.screen.get_rect().height
        self.area_barra = self.screen.subsurface(
            (0, 0), (self.screen_width, ALTURA_BARRA))
        self.playing_area = self.screen.subsurface(
            ((self.screen_width-self.screen_width)/2, ALTURA_BARRA), (self.screen_width, self.screen_height - ALTURA_BARRA))
        self.font = pygame.font.Font("fonts/VeraBd.ttf", 70)
        self.aplausos = pygame.mixer.Sound("sounds/aplauso.ogg")
        self.musica = pygame.mixer.Sound("sounds/menumusic22.ogg")
        grossini_instance = GrossiniSprite(self)
        self.imagenVida = grossini_instance.imagenes[0]
        self.barra = pygame.transform.scale(pygame.image.load(
            "images/barra.jpg").convert_alpha(), (self.screen_width, ALTURA_BARRA))

        self.letrasEncendidas = self.armarLetras(BASECOLOR, OUTLINECOLOR)
        self.letrasApagadas = self.armarLetras(OUTLINECOLOR, BASECOLOR)
        self.display = Display(self, self.area_barra.subsurface(
            (50, 50), (self.screen_width-100, 100)))
        pygame.mouse.set_visible(False)
        self.imagen_presentacion = pygame.image.load(
            "images/splash.jpg").convert()
        self.imagen_presentacion = pygame.transform.scale(
            self.imagen_presentacion, (self.screen_width, self.screen_height))
        self.show_image(self.imagen_presentacion, 3)
        while self.menu_to_game_loop:
            # Override the variable set byt credits for load_game_bool
            self.load_game_bool = True
            # Load the menu instance
            self.call_menu()

            # Load the game instance if it proceeds,
            # check the option selected is to show credits
            if self.load_game_bool:
                self.game_instance()
            else:
                self.load_game_bool = True


# SCRIPT RUNNER
if __name__ == "__main__":
    fbman = FalabracmanGame()
    fbman.run()
