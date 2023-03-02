# -*- coding: utf-8 -*-
"""
GEOZONE - gestion des zones.
@author: Jérôme Lacaille
"""
__date__ = "2023-02-24"
__version__ = '1.3'


import os, re
import numpy as np
import json

EARTHREP = 'data/zones/_Earth/'
EARTHDIR = os.path.join(os.path.dirname(__file__),EARTHREP)

# ---------------------------------------------------------------------
class GeofileException(ValueError):
    """ Exception raised when geofile is bad."""
    pass

# ---------------------------------------------------------------------
def zonelist(geomap = "map.geojson"):
    """ ZONELIST - Récupération de la liste des zones stockées."""

    if isinstance(geomap,dict):
        geolist = geomap
    else:
        with open(os.path.join(EARTHDIR,geomap)) as g:
            geolist = json.load(g)

    if 'type' not in geolist:
        raise GeofileException(f"No type in {geomap}.")
    if 'features' not in geolist:
        raise GeofileException(f"No feature in {geomap}.")

    Z = [getzone(geolist,i) for i in range(len(geolist['features']))]
    return Z


# ---------------------------------------------------------------------
def getzone(geolist,i=0):
    """GETZONE - Récupération des éléments d'intérêt d'une geozone."""
    
    if 'type' not in geolist:
        raise GeofileException("Geolist is not a geofile.")
    if geolist['type'] != 'FeatureCollection':
        raise GeofileException("Geolist['type'] is not a FeatureCollection.")

    n = len(geolist['features'])
    sz = "zones" if n>1 else "zone"
    assert i>=0, "Le numéro de zone doit être positif."
    assert i<n, f"La liste ne contient que {n} {sz}."

    G0 = geolist['features'][i]

    if 'properties' not in G0:
        raise GeofileException(f"No properties in geolist[{i}].")
    if 'geometry' not in G0:
        raise GeofileException(f"No geometry in geolist[{i}].")
    if 'coordinates' not in G0['geometry']:
        raise GeofileException(f"No coordinates in geolist[{i}]['geometry].")

    # Récupération des coordonnées.
    G = np.array(G0['geometry']['coordinates'][0])
    lon0,lat0 = G.min(axis=0)
    lon1,lat1 = G.max(axis=0)

    # Récupération du nom de la zone.
    if 'name' in G0['properties']:
        name = G0['properties']['name']
    else:
        name = f"Geozone [{lat0:.1f},{lon0:.1f},{lat1:.1f},{lon1:.1f}]"

    # Réponse.
    zone = dict(
        name = name,
        bbox = [lat0, lon0, lat1, lon1]
    )
    return zone

# ---------------------------------------------------------------------
class GeoZone:
    """ GEOZONE - Un objet contenant les zones géographiques et permettant de les manipuler.

    GeoZone est initié à partir d'un fichier issu de geojson.io. Par défaut, ce fichier est "map.geojson" et est situé dans le sous-répertoire "data/_Earth".
    """

    def __init__(self, geomap = "map.geojson"):
        """ Initialisation 
        
            L'initialisation a besoin de la zone géographique 
            et du nom de l'indicateur calculé.
        """
        
        self.Z = zonelist(geomap)
        self.index = 0
        
    def __len__(self):
        """ Le nombre de données. """
        return len(self.Z)
    
    def __getitem__(self, i):
        """ Récupère le  i-ième élément. """
        n = len(self.Z)
        if i<0 or i>=n:
            raise GeofileException(f"Zone inexistante, doit etre comprise entre entre 0 et {n-1}.")
        return self.Z[i]
        
    def __iter__(self):
        self.index = 0
        return self

    def __repr__(self):
        n = len(self.Z)
        sz = "GeoZones" if n>1 else "GeoZone"
        return f"Liste de {n} {sz}"
    
    def __next__(self):
        index = self.index
        if index==len(self.Z):
            raise StopIteration
        else:
            self.index = index+1
            return self[index]

    def coordinates(self, i):
        z = self.Z[i]
        return z['bbox']
    
    def bboxbyname(self, name):
        """ BBOXBYNAME - Récupération des coordonnées à partir du nom.
        """
        for z in self.Z:
            if z['name'] == name:
                return z['bbox']
        raise GeofileException(f"La zone {name} n'existe pas.")
    

