# -*- coding: utf-8 -*-
"""
OCLI - Outil d'extraction des données Optiques.

Votre travail est de construire ce module. Il correspond à la section 3
du notebook ocli_doc.ipynb.
J'ai quand même laissé quelques détails avec diverses explications
pour vous aider à démarrer.

@author: Jérôme Lacaille
"""

__date__ = "2023-02-25"
__version__ = '1.1'

import os
import re
from netCDF4 import Dataset
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import ipywidgets as widgets

# On importe l'objet GeoZone pour pouvoir dériver la classe Ocli
from .geozone import EARTHDIR, GeoZone

FCOVERDIR = ...


def getncfiles():
    """ GETNCFILES - Récupération sous la forme d'une table (FILE, REVISION) 
        indexée par la date des fichiers .nc.

        Quand deux fichiers ont la même date, on ne conserve que celui correspondant à la révision la plus grande.

        La table de sortie sera triée par l'index de date.
    """
    ...
    return df

# -------------------------------------------------------------------------
class Ocli(GeoZone):
    """ Ocli - Un objet définissant des zones géographiques et leur
        correspondance graphique.

        Cette classe dérive de GeoZone, il faut donc faire appel au constructeur de la classe mère, c'est assez facile en Python par l'appel de la fonction super().

        On va aussi compléter la méthode système d'affichage __repr__ pour différentier de la classe de base (testez pour voir sans cette méthode).
    """
    def __init__(self, geomap="map.geojson"):
        """ Initialise la classe GeoZone, puis récupère la liste des fichiers.
        """
        super().__init__(geomap)
        
        # On stocke la liste des noms de zones.
        self.geomap = geomap
        self.names = ...

        # Récupération de la liste des fichiers.
        self.df = getncfiles()
        self.dates = ...
    
    def __repr__(self):
        """ Affichage de base de l'objet Ocli.
        """
        return f"Ocli ({self.geomap}) - " + super().__repr__()
    
    def ncfilebydate(self, date):
        """ Récupère le nom du fichier associé à une date.
        """
        ...
        i = ...
        return self.df.FILE[i]

    def values(self,date,name):
        """ Récupère le tableau des données.
        """
        lat0,lon0,lat1,lon1 = ...
        fname = ...

        with Dataset(fname, 'r') as nc:
            # Cacul des coordonnées utiles.
            lon = ...
            lat = ...

            # Extraction des données FCOVER.
            ...
            ...
            fc = ...

            # On gère le masque par des NaN.
            F = fc.data
            F[fc.mask] = np.nan
        
        return F

    def plot(self,date,name):
        """ Affiche une zone.
        """
        F = self.values(date,name)
        ...

    def iplot(self):
        """ Affichage interactif.
        """
        ...