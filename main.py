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
        template_values = {'fitness': get_from_cache(), 'locations': locations}
        result_template = jinja_environment.get_template('result.html')

        self.response.out.write(result_template.render(template_values))

    def rst(self):
        print >>sys.stdout, "Reset.."
        q = taskqueue.Queue('pull-queue')

        #Hack to make sure, all entries in the queue are deleted in local mode
        #tasks = q.lease_tasks(3600, 20, 1)
        #q.delete_tasks(tasks)

        #for _ in range(100):
        #    q.purge()

        q.purge()

        reset_cache()


    def post(self):
        """
        Init workers on a push queue.
        """

        reset = self.request.get('reset')
        problem = self.request.get('problem')

        if reset == '1':
            self.rst()
            self.redirect('/')

        elif problem != '':
            self.rst()

            global locations
            global config

            locations = parse_instance(problem)
            config = {'locations': locations}

            self.redirect('/')

        else:
            number_of_tasks = int(self.request.get('numb'))



            #q = taskqueue.Queue('pull-queue')
            #tasks = q.lease_tasks(3600, 1)

            #q.delete_tasks(tasks)



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