#!/usr/bin/env python
import jinja2
import os
import webapp2
from google.appengine.api import taskqueue

import random
from util import *
import json
import sys, time

class ResultHandler(webapp2.RequestHandler):
    """
    Handling for basic path "/"
    """

    def get(self):
        """
        Get the page with the current best results and a possibility to add individuals
        """
        starting = memcache.get('starttime')
        lasting = memcache.get('lasttime')
        current = 0
        if starting is not None and lasting is not None:
            current = lasting - starting
        template_values = {'fitness': get_from_cache(), 'locations': locations, 'result_time': current}
        result_template = jinja_environment.get_template('result.html')

        self.response.out.write(result_template.render(template_values))

    def reset(self):
        q = taskqueue.Queue('pull-queue')
        q.purge()
        reset_cache()

    def post(self):
        """
        Init workers on a push queue.
        """

        do_reset = self.request.get('reset')
        problem = self.request.get('problem')
        steps = self.request.get('steps')

        if do_reset == '1':
            self.reset()
            self.redirect('/')

        else:
            if problem != '':

                global locations
                global config

                locations = parse_instance(problem)
                config = {'locations': locations}

            number_of_tasks = int(self.request.get('numb'))
            if not memcache.set("steps", int(steps)):
                logging.error('Memcache set failed.')

            if not memcache.set("starttime", time.time()):
                logging.error('Memcache set failed.')

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
        save_to_cache(fit)

    def get(self):
        self.response.out.write(running)

running = 1
reset_cache()
# TODO Have a possibility of adding a custom new problem. File upload?
# also only write to database in the end of computation or add to push queue
locations = parse_instance("https://dl.dropboxusercontent.com/u/218741/a280.tsp")

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

config = {'locations': locations}

app = webapp2.WSGIApplication([('/', ResultHandler),
                               ('/worker', ResultWorker)],
                              debug=True, config=config)