from google.appengine.api import taskqueue
from google.appengine.api import background_thread
import json
import random
from util import fitness, txn, distance
from google.appengine.ext import db


def transpose(ind1, ind2):
    """
    Adds a subroute to the best location of the other individual
    """
    rfrom = random.randint(0, len(ind1) - 1)
    rto = random.randint(rfrom + 1, len(ind1))
    subroute = ind1[rfrom:rto]

    new = ind2[:]
    for i in ind2:
        if i in subroute:
            new.remove(i)

    whereto = new[0]
    l = len(subroute)
    mindistance = distance(new[0][1], new[0][2], subroute[l-1][1], subroute[l-1][2])
    for i in new:
        newdistance = distance(i[1], i[2], subroute[l-1][1], subroute[l-1][2])
        if newdistance < mindistance:
            whereto = i
            mindistance = newdistance

    new = new[0: new.index(whereto)] + subroute + new[new.index(whereto):len(new)]
    return new


def swap(old):
    """
    Exchanges 2 clients
    """
    ind = old[:]
    client1 = random.randint(0, len(ind) - 1)
    client2 = random.randint(0, len(ind) - 1)

    tmp = ind[client1]
    ind[client1] = ind[client2]
    ind[client2] = tmp

    return ind


def mutate():
    """
    Function responsible for the mutation
    """
    queue = taskqueue.Queue('pull-queue')

    # we take one task
    tasks = queue.lease_tasks(3600, 1)

    #if any task was taken
    if len(tasks) > 0:
        old = json.loads(tasks[0].payload)
        new = swap(old)
        newtasks = []
        if fitness(old) < fitness(new):
            payload_str = json.dumps(old)
        else:
            payload_str = json.dumps(new)

        newfit = fitness(new)
        print "Mutation", fitness(new)
        # we can't save it to the database
        #db.run_in_transaction(txn, newfit)

        newtasks.append(taskqueue.Task(payload=payload_str, method='PULL'))
        queue.delete_tasks(tasks)
        queue.add(newtasks)


def cross():
    """
    Function responsible for the cross-over
    """
    queue = taskqueue.Queue('pull-queue')

    # we take one task
    tasks = queue.lease_tasks(3600, 2)

    if len(tasks) == 2:
        ind1 = json.loads(tasks[0].payload)
        ind2 = json.loads(tasks[1].payload)
        child1 = transpose(ind1, ind2)
        child2 = transpose(ind2, ind1)

        # we choose the 2 best
        possible = [ind1, ind2, child1, child2]
        fits = [fitness(ind1), fitness(ind2), fitness(child1), fitness(child2)]

        best = max(fits)
        ret1 = possible[fits.index(best)]
        possible.remove(ret1)
        fits.remove(best)

        best = max(fits)
        ret2 = possible[fits.index(best)]
        possible.remove(ret2)
        fits.remove(best)

        # we can't save it to the database
        #newfit = fitness(ret1)
        # we can't save it to the database
        #db.run_in_transaction(txn, newfit)

        #newfit = fitness(ret2)
        # we can't save it to the database
        #db.run_in_transaction(txn, newfit)

        newtasks = []
        print "Crossover", fitness(ret1), fitness(ret2)

        newtasks.append(taskqueue.Task(payload=json.dumps(ret1), method='PULL'))
        newtasks.append(taskqueue.Task(payload=json.dumps(ret2), method='PULL'))

        queue.delete_tasks(tasks)

        queue.add(newtasks)

    elif len(tasks) == 1:
        #return tasks
        queue.delete_tasks(tasks)
        queue.add([taskqueue.Task(payload=tasks[0].payload, method='PULL')])


def f():
    while True:
        if random.random() > 0.5:
            mutate()
        else:
            cross()

# starts the background thread that randomly mutates of crossovers
t = background_thread.BackgroundThread(target=f)
t.start()



