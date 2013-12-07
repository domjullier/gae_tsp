__author__ = 'easyrider'

import math

def getEuc2D_distance(ix, iy, jx, jy):
    xd = ix - jx
    yd = iy - jy

    dij = math.sqrt(xd*xd + yd*yd)

    return dij

