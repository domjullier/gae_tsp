#!/usr/bin/env python
import jinja2
import os
import webapp2
from google.appengine.api import taskqueue
from google.appengine.ext import db
import random
from util import fitness, txn
from models import Result
import json


class ResultHandler(webapp2.RequestHandler):
    """
    Handling for basic path "/"
    """

    def get(self):
        """
        Get the page with the current best results and a possibility to add individuals
        """
        result = Result.get_by_key_name('best')
        if result is not None:
            fit = result.fitness
        else:
            fit = None
        template_values = {'fitness': fit, 'locations': locations}
        result_template = jinja_environment.get_template('result.html')

        self.response.out.write(result_template.render(template_values))

    def post(self):
        """
        Init workers on a push queue.
        """
        number_of_tasks = int(self.request.get('numb'))
        # @TODO purge a taskqueue when uploading new problem
        # Add given number of calculation taks to the queue
        for _ in range(0, number_of_tasks):
            taskqueue.add(url='/worker')

        self.redirect('/')


class ResultWorker(webapp2.RequestHandler):
    """
    Handling for path "/worker"
    """

    def generate_random_path(self):
        """
        Generates a new random solution as a permutation of all the locations
        """
        random_path = self.app.config.get('locations')
        random.shuffle(random_path)
        return random_path

    def post(self):
        """
        Use it to create solutions instances ( our "individuals")
        Should run at most 1/s
        """
        path = self.generate_random_path()

        #calculate fitness for our solution
        fit = fitness(path)

        q = taskqueue.Queue('pull-queue')
        tasks = []

        payload_str = json.dumps(path)

        tasks.append(taskqueue.Task(payload=payload_str, method='PULL'))
        q.add(tasks)

        #db.run_in_transaction(txn, fit)


def int_elems(l):
    return [int(i.strip()) for i in l.split(' ') if i != '']


def reset_db():
    query = Result.all(keys_only=True)
    entries = query.fetch(1000)
    db.delete(entries)


def parse_instance(file_name):
    with open(file_name) as src:
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


reset_db()
# TODO Have a possibility of adding a custom new problem. File upload?
# also only write to database in the end of computation or add to push queue
locations = parse_instance("a280.tsp")

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

config = {'locations': locations}

app = webapp2.WSGIApplication([('/', ResultHandler),
                               ('/worker', ResultWorker)],
                              debug=True, config=config)