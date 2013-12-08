import math


def distance(ix, iy, jx, jy):
    """
    Distance in cartesian coordinates
    """
    xd = ix - jx
    yd = iy - jy
    dij = math.sqrt(xd*xd + yd*yd)
    return dij


def fitness(path):
    """
    Total distance on a path
    """
    last = path[0]
    dist = 0
    for city in path[1:]:
        dist += distance(last[1], last[2], city[1], city[2])
        last = city

    return dist