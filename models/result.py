from google.appengine.ext import db


class Result(db.Model):
    """
    Represents current best solution
    """
    fitness = db.FloatProperty(indexed=False)
    #solution = db.ListProperty(indexed=False)