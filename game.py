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
from random import randrange
from olpcgames import pausescreen
import random
import hollow
from init import screen
from config import *

FBM_SPEED = 15
ALTURA_BARRA = 150

screen_width = screen.get_rect().width
screen_height = screen.get_rect().height
area_barra = screen.subsurface( (0,0), (screen_width, ALTURA_BARRA) )
playing_area = screen.subsurface( (0,ALTURA_BARRA), (screen_width, screen_height - ALTURA_BARRA) )
font = pygame.font.Font("fonts/VeraBd.ttf", 70)
aplausos = pygame.mixer.Sound("sounds/aplauso.ogg")
musica = pygame.mixer.Sound("sounds/menumusic22.ogg")

class EndOfGame(Exception):
    pass

class VoceGanhou(EndOfGame):
    imagen_ganaste = pygame.image.load("images/ganaste.png").convert_alpha()
    def accion(self):
        aplausos.play()
        estado.mensaje(self.imagen_ganaste)

class VocePerdeu(EndOfGame):
    imagen_perdiste = pygame.image.load("images/perdio.png").convert_alpha()
    def accion(self):
        estado.mensaje(self.imagen_perdiste)

class GrossiniSprite(pygame.sprite.Sprite):
    SPEED = FBM_SPEED
    imagenes = [ pygame.image.load("images/zeek%d.png"%n).convert_alpha() for n in range(12) ]
    image = imagenes[0]
    aplauso = pygame.mixer.Sound("sounds/aplauso.ogg")

    ciclosCaminata = dict(
        izquierda = [ 4, 5, 4, 6 ],
        derecha = [ 1, 2, 1, 3 ],
        arriba = [ 9, 10, 9, 11 ],
        abajo = [ 0, 7, 0, 8 ],
    )
    velocidades = dict(
        izquierda = (-1, 0),
        derecha = (1, 0),
        arriba = (0, -1),
        abajo = (0, 1),
    )

    def __init__(self):
        self.hundido = False
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect(topright=playing_area.get_rect().topright)
        self.cuadros = self.ciclosCaminata["abajo"]
        self.frenar()

    def frenar(self):
        self.velocidad = (0,0)
        self.numeroCuadro = 0

    def step(self):
        dx, dy = self.velocidad
        self.image = self.imagenes[self.cuadros[self.numeroCuadro]]
        if dx != 0 or dy != 0:
            self.numeroCuadro = (self.numeroCuadro + 1) % 4
            self.rect.move_ip((dx*self.SPEED, dy*self.SPEED))
            if not playing_area.get_rect().contains(self.rect):
                self.rect.clamp_ip( playing_area.get_rect() )
                self.frenar()

    def mirar(self, direccion):
        self.cuadros = self.ciclosCaminata[direccion]
        self.velocidad = self.velocidades[direccion]
        self.numeroCuadro = 0

imagenVida = GrossiniSprite.imagenes[0]

class Collisionable(pygame.sprite.Sprite):
    def __init__(self, otros):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect()
        colisiona = True
        contador = 99
        while colisiona and contador > 0:
            self.rect.center = (randrange(playing_area.get_rect().width), randrange(playing_area.get_rect().height))
            self.rect.clamp_ip( playing_area.get_rect() )
            contador -= 1
            colisiona = False
            for g in otros:
                if pygame.sprite.spritecollide(self, g, False):
                    colisiona = True

def armarLetras(color1, color2):
    d = {}
    for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZÑÃÇÕ*":
        d[l] = hollow.textOutline(font, l, color1, color2)
    return d
    
letrasEncendidas = armarLetras(BASECOLOR, OUTLINECOLOR)
letrasApagadas = armarLetras(OUTLINECOLOR, BASECOLOR)

def dameLetra(dictLetras, letra):
    return dictLetras.get(letra, dictLetras["*"])
    
class LetterSprite(Collisionable):
    sound =  pygame.mixer.Sound("sounds/money.ogg")
    def __init__(self, grossini, letra):
        self.image = dameLetra(letrasEncendidas, letra)
        self.letra = letra
        Collisionable.__init__(self, grossini)

class Lago(Collisionable):
    sound = pygame.mixer.Sound("sounds/splash.ogg")
    imagenes = [ pygame.image.load("images/lago%d.png"%n).convert_alpha() for n in [0,1,2,3] ]
    def __init__(self, *a):
        self.image = random.choice(self.imagenes)
        Collisionable.__init__(self, *a)

class Display:
    def __init__(self, area):
        self.area = area
        self.vidas = 0
        self.setDisplay("")

    def setDisplay(self, palabra):
        self.palabra = palabra
        self.encendidas = 0
        self.dibujar()

    def setVidas(self, vidas):
        self.vidas = vidas
        self.dibujar()

    def dibujar(self):
        area_barra.blit(barra, (0,0))
        w = 0
        for n, l in enumerate(self.palabra):
            if n >= self.encendidas:
                imagen = dameLetra(letrasApagadas, l)
            else:
                imagen = dameLetra(letrasEncendidas, l)
            self.area.blit(imagen, (w,0))
            w += imagen.get_rect().width

        w = self.area.get_rect().width
        for n in range(self.vidas):
            self.area.blit(imagenVida, (w,0))
            w -= imagenVida.get_rect().width
    
    def encender(self):
        self.encendidas += 1
        self.dibujar()
        
barra = pygame.image.load("images/barra.jpg").convert_alpha()

class Palabra(pygame.sprite.Group):
    def __init__(self, palabra, groupsinni, lagos):
        pygame.sprite.Group.__init__(self)
        for letra in palabra.strip():
            self.add(LetterSprite([groupsinni, lagos, self], letra))

class Lagos(pygame.sprite.Group):
    def __init__(self, numLagos, groupsinni):
        pygame.sprite.Group.__init__(self)
        for n in range(numLagos):
            self.add(Lago([groupsinni, self]))


display = None
estado = None

class Nivel:
    base_fondo = pygame.image.load("images/fondo.jpg").convert()
    def __init__(self, numero, dic, grossini, groupsinni):
        self.fondo = self.base_fondo.copy()
        self.finNivel = False
        self.palabras = [ dic.getRandomWordByCategory().upper().encode("iso8859-1") for n in range(numero) ]
        self.numero = numero
        self.grupoLagos = Lagos(5, groupsinni)
        self.groupsinni = groupsinni
        self.grupoLagos.draw(self.fondo)
        self.nuevaPalabra(grossini)
        playing_area.blit(self.fondo, (0,0))

    def nuevaPalabra(self, grossini):
        self.palabra = self.palabras.pop()
        self.grupoLetras = Palabra(self.palabra, self.groupsinni, self.grupoLagos)
        self.encontradas = []
        display.setDisplay(self.palabra)
        playing_area.blit(self.fondo, (0,0))

    def dibujar(self, area):
        self.grupoLetras.clear(area, self.fondo)  
        self.grupoLetras.draw(area)  

    def hayMasPalabras(self):
        return len(self.palabras) > 0

    def verificarColisiones(self, grossini):
        charcos_colisionados = pygame.sprite.spritecollide(grossini,self.grupoLagos,False)
        letras_colisionadas = pygame.sprite.spritecollide(grossini,self.grupoLetras,False)

        if charcos_colisionados:
            Lago.sound.play()
            grossini.hundido = True

        if letras_colisionadas:
            for l in letras_colisionadas:
                if l.letra == self.palabra[len(self.encontradas)]:
                    self.encontradas.append(l.letra)
                    #grossini.frenar()
                    self.grupoLetras.remove(l)
                    LetterSprite.sound.play()
                    display.encender()
                    if len(self.encontradas) == len(self.palabra):
                        if self.hayMasPalabras():
                            self.nuevaPalabra(grossini)
                        else:
                            self.finNivel = True 

class Estado:
    def __init__(self, dic):
        self.dic = dic
        self.nroNivel = 0
        self.nivelMaximo = 1
        self.setVidas(VIDAS)
        self.groupsinni = None
        self.resetGrossini()
        self.avanzarNivel()

    def resetGrossini(self):
        if self.groupsinni is not None:
            self.groupsinni.clear(playing_area, self.nivel.fondo)
        self.grossini = GrossiniSprite()
        #aca karucha
        self.groupsinni = pygame.sprite.Group()
        self.groupsinni.add(self.grossini)

    def avanzarNivel(self):
        self.nroNivel += 1
        self.nivel = Nivel(self.nroNivel, self.dic, self.grossini, self.groupsinni)
        aplausos.play()

    def dibujar(self, area):
        self.groupsinni.clear(area, self.nivel.fondo)
        self.nivel.dibujar(area)
        self.groupsinni.draw(area)

    def setVidas(self, vidas):
        self.vidas = vidas
        display.setVidas(vidas)

    def mensaje(self, msg):
        playing_area.blit(msg, msg.get_rect(center = playing_area.get_rect().center))
        pygame.display.flip()
        pygame.time.delay(4000)

    def step(self):
        self.grossini.step()
        self.nivel.verificarColisiones(self.grossini)
        if self.grossini.hundido:
            self.setVidas(self.vidas-1)
            self.resetGrossini()
        if self.nivel.finNivel:
            if self.nivel.numero > self.nivelMaximo:
                raise VoceGanhou()
            self.avanzarNivel()

        if self.vidas == 0:
            raise VocePerdeu()

def main(language="bra"):
    import paladict
    dic = paladict.PalaDict(language)

    global display
    display = Display(area_barra.subsurface((50,50), (screen_width-100,100)))
    global estado
    estado = Estado(dic)
    #Comienza el juego
    playing = True
    clock = pygame.time.Clock()
    
    #musica.play(-1)

    while playing:
        clock.tick(20)
        for event in pausescreen.get_events(DEMORA_PAUSA):
            if event.type == QUIT:
                playing = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    playing = False
                elif event.key in [K_UP, K_KP8, K_KP9]:
                    estado.grossini.mirar("arriba")
                elif event.key in [K_DOWN, K_KP2, K_KP3]:
                    estado.grossini.mirar("abajo")
                elif event.key in [K_LEFT, K_KP4, K_KP7]:
                    estado.grossini.mirar("izquierda")
                elif event.key in [K_RIGHT, K_KP6, K_KP1]:
                    estado.grossini.mirar("derecha")
        try:
            estado.step()
        except EndOfGame, e:
            e.accion()
            break

        estado.dibujar(playing_area)
        pygame.display.flip()

    #musica.stop()

if __name__ == "__main__":
    main()
