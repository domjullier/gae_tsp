#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import jinja2
import os
import webapp2
from google.appengine.api import taskqueue
from google.appengine.ext import db
import random

class Result(db.Model):
    fitness = db.IntegerProperty(indexed=False)
    #add best solution

class ResultHandler(webapp2.RequestHandler):

    def generate_random_path(self):
        locations = self.app.config.get('locations')

        random_path = random.sample(range(len(locations)), len(locations))

        return random_path

    def get(self):
        result = Result.get_by_key_name('a')

        if result is not None:
            fitness = result.fitness
        else:
            fitness = None

        template_values = {'fitness': fitness, 'locations': locations}
        result_template = jinja_environment.get_template('result.html')

        self.response.out.write(result_template.render(template_values))

    def post(self):


        number_of_tasks = int(self.request.get('numb'))

        # Add given number of calculation taks to the queue
        for _ in range(0, number_of_tasks):
            path = self.generate_random_path()

            taskqueue.add(url='/worker', params={'path': path})

        self.redirect('/')




class ResultWorker(webapp2.RequestHandler):
    def post(self): # should run at most 1/s
        path = self.request.get_all('path')

        def txn(fitness):
            result = Result.get_by_key_name('a')
            if result is None:
                result = Result(key_name='a', fitness=fitness)
            elif result.fitness>fitness:
                result.fitness = fitness

            result.put()

        #calculate
        #TODO fitness function
        fitness = int(path[0]) + int(path[1])

        print 'fitness'
        print fitness

        db.run_in_transaction(txn, fitness)


def intElems(L):
    return ([int(i.strip()) for i in L.split(' ') if i != ''])


def reset_db():
    query = Result.all(keys_only=True)
    entries =query.fetch(1000)
    db.delete(entries)


def parse_instance(fName):
    with open(fName) as src:
        lines = src.readlines()

        dim = int(lines[3].split(' ')[1])

        print dim

        locations = []

        for i in range(6, dim+6):
            current_line=lines[i].split()
            locations.append([int(current_line[0]), int(current_line[1]), int(current_line[2])])

        #print locations[0]
        #print locations[279]

        return locations

reset_db()
locations = parse_instance("a280.tsp")


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

config = {'locations': locations}


app = webapp2.WSGIApplication([('/', ResultHandler),
                              ('/worker', ResultWorker)],
                              debug=True, config=config)