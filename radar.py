# -*- coding: utf-8 -*-
"""
RADAR - gestion des données radar.
@author: Jérôme Lacaille
"""
__date__ = "2023-02-28"
__version__ = '1.0'


import os
import numpy as np
import pandas as pd
import datetime as dt
from xml.etree import ElementTree
from scipy.interpolate import griddata

# ---------------------------------------------------------------------
def rviquery(zone):
    """ Renvoie la requête à appliquer à  Sentinel Hub. 
        Convertie la bbox en une requête "Contains(POLYGON(...))"
    """
    
    bbox = zone['bbox']
    query = '(footprint:"Contains(' +\
        'POLYGON(({1:.3f} {0:.3f},{3:.3f} {0:.3f},{3:.3f} {2:.3f},{1:.3f} {2:.3f},{1:.3f} {0:.3f}))'.format(*bbox) +\
        ')") AND  ((platformname:Sentinel-1 AND producttype:GRD))'

    return query

# ---------------------------------------------------------------------
def getllmask(zone,desc,code,STEP=5):
    """ Création du masque des pixels de la zone sur la sous-image. 

        Le paralmètre STEP est une valeur de précision pour la sous région rectangulaire encadrant la zone en coordonnées orbitales. On encadre plus largement en augmentant STEP et cela diminue très fortement le temps de calcul au prix de plus de mémoire à stocker.
    """
    
    # Calcul de la bbox minimale.
    heigth = desc['heigth']
    width = desc['width']

    # On recherche sur un box plus fruste.
    grid_x, grid_y = np.mgrid[0:heigth-1:STEP, 0:width-1:STEP]
    points = code[['line','pixel']].values
    latitude = code['lat'].values
    Lat = griddata(points, latitude, (grid_x, grid_y), method='linear')
    longitude = code['lon'].values
    Lon = griddata(points, longitude, (grid_x, grid_y), method='linear')

    # Le masque
    lat0,lon0,lat1,lon1 = zone['bbox']
    Mask = (Lat>=lat0) & (Lat<=lat1) & (Lon>=lon0) & (Lon<=lon1)

    # Calcul de la parralaxe en latitude et longitude
    dlat = (lat1+lat0)/2 - (latitude.max()+latitude.min())/2
    dlon = (lon1+lon0)/2 - (longitude.max()+longitude.min())/2
    
    # Recherche d'une sous-région pas trop grosse encadrant zone
    ux = np.argwhere(Mask.any(axis=0))
    minx = int(max(STEP*(ux.min()-STEP),0))
    maxx = int(min(STEP*(ux.max()+STEP),width))

    uy = np.argwhere(Mask.any(axis=1))
    miny = int(max(STEP*(uy.min()-STEP),0))
    maxy = int(min(STEP*(uy.max()+STEP),heigth))

    # Calcul de la parallaxe sur les axes orbitaux
    dx = (maxx+minx)/2 - width/2
    dy = (maxy+miny)/2 - heigth/2

    # Le masque sur l'extraction
    grid_x, grid_y = np.mgrid[miny:maxy, minx:maxx]
    lat = griddata(points, latitude, (grid_x, grid_y), method='linear')
    lon = griddata(points, longitude, (grid_x, grid_y), method='linear')
    belong = (lat>=lat0) & (lat<=lat1) & (lon>=lon0) & (lon<=lon1)
    
    # Calcul de l'angle moyen d'incidence.
    incidence = code['incidence'].values
    incgrid = griddata(points, incidence, (grid_x, grid_y), method='linear')
    inc = np.nanmean(incgrid[belong])
    
    # Calcul de l'angle moyen d'élévation.
    elevation = code['elevation'].values
    elegrid = griddata(points, elevation, (grid_x, grid_y), method='linear')
    ele = np.nanmean(elegrid[belong])
    
    mask = dict(bbox=(minx, miny, maxx, maxy),
                incidence=inc, elevation=ele,
                dvec=(dlat,dlon), dxy=(dx,dy),
                lat=lat, lon=lon, belong=belong)

    return mask

# ---------------------------------------------------------------------
def imgnorm(img, p):
    """ Normalise une image entre deux quantiles. """
    
    if p>0:
        q0,q1 = np.quantile(img,[p,1-p])
    else:
        q0,q1 = img.min(), img.max()
    delta = float(q1-q0)
    fimg = (1.0*img-q0)/delta
    fimg[fimg>1.0] = 1.0
    fimg[fimg<0.0] = 0
    return fimg