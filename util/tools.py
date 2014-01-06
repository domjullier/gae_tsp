import math
from models import Result
from google.appengine.api import memcache
import logging
from google.appengine.ext import db
import urllib2, time


def reset_db():
    query = Result.all(keys_only=True)
    entries = query.fetch(1000)
    db.delete(entries)


def parse_instance(file_name):
    """
    Parsing the problem instance
    """

    src = urllib2.urlopen(file_name)

    lines = src.readlines()

    dim = int(lines[3].split(' ')[1])

    #print dim
    cities = []

    for i in range(6, dim + 6):
        current_line = lines[i].split()
        cities.append([int(current_line[0]), int(current_line[1]), int(current_line[2])])

    #print locations[0]
    #print locations[279]

    return cities


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


def txn(fit):
    result = Result.get_by_key_name('best')
    if result is None:
        result = Result(key_name='best', fitness=fit)
    elif result.fitness > fit:
        result.fitness = fit
    result.put()


def save_to_cache(fit):
    """
    Adding value to memcache
    """
    best = memcache.get('best')
    if best is not None:
        if fit < best:
            if not memcache.set('best', fit):
                logging.error('Memcache set failed.')
    else:
        if not memcache.set('best', fit):
            logging.error('Memcache set failed.')


def get_from_cache():
    return memcache.get('best')


def get_and_update():
    steps = memcache.get("steps")
    if steps is not None and steps is not 0:
        if not memcache.set("steps", steps-1):
            logging.error('Memcache set failed.')
        if not memcache.set("lasttime", time.time()):
                logging.error('Memcache set failed.')
    return steps


def reset_cache():
    memcache.delete('best')
