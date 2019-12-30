# -*- coding: iso-8859-1 -*-
# Copyright (C) 2008 by Achuras Experience
#
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


import os
import random
import codecs


class PalaDict:
    def __init__(self, language):
        PALADICTIONARY = os.getcwd()+"/data/"+language+"/dict.txt"
        #infile = codecs.open( PALADICTIONARY, "r" ,  "iso-8859-1")
        infile = open(PALADICTIONARY, "r")
        palabracman_dict = dict()
        for line in infile:
            # Creo nueva categoria en el diccionario
            if line[0] == '-':
                current_category = line[1:]
                palabracman_dict[current_category] = list()
            else:
                palabracman_dict[current_category].append(line[1:])

        self.palabracman_dict = palabracman_dict
        infile.close()

    def getDictionary(self):
        return self.palabracman_dict

    def getRandomWordByCategory(self):
        dictionaryCategory = self.palabracman_dict["Palabras\n"]
        randomWordIndex = random.randint(0, (dictionaryCategory.__len__()-1))
        return dictionaryCategory[randomWordIndex].rpartition("\n")[0]


if __name__ == "__main__":
    e = PalaDict("en")
    print(e.getRandomWordByCategory())
    # print e.getDictionary()
