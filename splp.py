#!/usr/bin/env python2
# -*- coding: utf8 -*-

'''
Created on Oct 29, 2013

@author: easyrider
'''
import random



class Params():
    poolSize        = 50
    mutationProb    = 0.2
    simSteps        = 500

    crossOver       = 'OnePoint' # OnePoint
    uniformRatio    = 0.5

    mutationType    = 'BitFlip' # BitFlip

                        #F1  F2  F3  F4
    plantsDef       = [[ 10, 30, 40, 15], #C1
                       [ 40, 20, 50, 12], #C2
                       [ 10, 24, 30, 30]] #C3

    plantsCosts     = [30, 20, 40, 15]


    plantsN         = len(plantsCosts)
    clientsN        = len(plantsDef)

    selectMethod    = "Tournament"
    tournmntSize    = 2
    
    mutation15Thresh    = 0.2 #should be nearly always 1/5
    generations15 = 5 #edfines, over how many generations the the apative rule is checked and applied
    
    #plantsDef[C][P]
    


def intElems(L):
    return ([int(i.strip()) for i in L.split(' ') if i != ''])

def euclidParse(fName):
    with open(fName) as src:
        lines = src.readlines()

        dim, fix = (intElems(lines[2]))

        M = [ [1000000] * dim for _ in xrange(dim) ]

        for i in xrange(4, len(lines)):
            p, c, cost = intElems(lines[i])
            M[c-1][p-1] = cost
        
        Params.plantsDef = M
        Params.plantsCosts = [fix] * dim

        Params.plantsN = len(Params.plantsCosts)
        Params.clientsN = len(Params.plantsDef)




# TODO
# Selekcja zwraca za mało osobników, powinna poolSize (matingPoolSize należy
# usunąć). Mutacja powinna działać z jakimś małym prawdopodobieństwem
# na każdy z osobników potomnych (stworzonych przez krzyżowanie z 
# wyselekcjonowanych)


class Genotype():

    genoType = []

    def __init__(self, genotype = None):
        if genotype is None:
            self.genoType = random.sample(
                    range(Params.plantsN), random.randint(1, Params.plantsN))
        else:
            self.genoType = genotype
        self.genoType.sort()


    def getGenoType(self):
        return self.genoType


    def getFitness(self):
        #print("self.genoType: {}".format(self.genoType))
        fitNess = 0
        for c in xrange(Params.clientsN):
            cliCost = [Params.plantsDef[c][p] for p in self.genoType]
            #print("cliCost: {}".format(cliCost))
            fitNess += min(cliCost)
            #print("fitNess: {}".format(fitNess))

        for p in self.genoType:
            fitNess += Params.plantsCosts[p]
        #print("Total fitNess: {}".format(fitNess))

        return fitNess


    def crossOverOnePoint(self, other):
    
        #find facility with lowest and highest number
        lowest=self.getGenoType()[0]
        
        if lowest>other.getGenoType()[0]:
            lowest=other.getGenoType()[0]
            
        
        highest=self.getGenoType()[len(self.getGenoType())-1]
        
        if highest<other.getGenoType()[len(other.getGenoType())-1]:
            highest=other.getGenoType()[len(other.getGenoType())-1] 

        cutPt = 10#random.randint(lowest, highest)
        
        #print('cutPt:{}'.format(cutPt))
        #remove everything after the cutPt from self genotype
        newGen=[]
        for fac in range(0, len(self.getGenoType())):
            if (self.getGenoType()[fac]<cutPt):
                pass
            else:
                #print(fac)
                newGen=self.getGenoType()[:fac]
                break;
                
        
                
        #add all elements after the cutPt from other genotype
        for fac in range(0, len(other.getGenoType())):
            
            if other.getGenoType()[fac]<cutPt:
                pass
            else:
                #print(fac)
                newGen=newGen + other.getGenoType()[fac:]
                break;
              
                
        
        
        return Genotype(newGen)


    def crossOver(self, other):

        if Params.crossOver == 'OnePoint':
            return self.crossOverOnePoint(other)

        else:
            raise Exception('Unknown crossover type: {}!'.
                    format(Params.crossOver))



    def mutateByBitFlip(self):
        genoTypeL = len(self.genoType)

        if genoTypeL == 1 or (genoTypeL < Params.plantsN and
                random.random() < 0.5): # wstawianie fabryki

            plantToInsert = random.choice([p for p in xrange(Params.plantsN) 
                    if p not in self.genoType])
            #print("Wstawianie: {}".format(plantToInsert))

            i = 0
            for i in xrange(len(self.genoType)):
                if plantToInsert < self.genoType[i]:
                    break
            else:
                i+=1
            #print("Wstawianie na pozycji: {}".format(i))
            self.genoType.insert(i, plantToInsert)

        else: # usuwanie fabryki
            elemToDel = random.randint(0, len(self.genoType)-1)
            #print("Usuwanie elementu: {}".format(elemToDel))
            del self.genoType[elemToDel]
        #print("self.genoType: {}".format(self.genoType))


    def mutate(self):
        if Params.mutationType == 'BitFlip':
            return self.mutateByBitFlip()

        else:
            raise Exception('Unknown mutation type: {}!'
                    .format(Params.mutationType))
            

### End of Genotype


def unrealKey(a):
    return a[1]

def selectByUnreal(pool, fits, nPoolSize, tournmntSize):
    newPool = []
    zipPool = zip(pool, fits)
    #print("pool: {}".format(pool))
    #print("fits: {}".format(fits))
    #print("zipPool: {}".format(zipPool))

    for _ in xrange(nPoolSize):
        tour = []
        for _ in xrange(tournmntSize):
            tour.append(random.choice(zipPool))

        winNer = max(tour, key = unrealKey)
        newPool.append(winNer[0])
    
    return newPool

def selectRoulette(population, fitnesses):
    populationN = len(population)
    #print('fitnesses: {}'.format(fitnesses))
    #fitnesses = [float(gen.getFitness()) for gen in self._population]
    total_fitness = float(sum(fitnesses))
    #print('total_fit: {}'.format(total_fitness))
    rel_fitness = [f/total_fitness for f in fitnesses]
    #print('rel_fit: {}'.format(rel_fitness))
    # Generate probability intervals for each individual
    probs = [sum(rel_fitness[:i+1]) for i in range(len(rel_fitness))]
    #print('probs: {}'.format(probs))
    # Draw new population
    new_population = []
    for n in xrange(populationN):
        r = random.random()
        for (i, individual) in enumerate(population):
            if r <= probs[i]:
                new_population.append(individual)
                #remove genotype and its probability rate from old population
                del probs[i]
                population.remove(individual)
                break
    #add rest of population which would not be attend in crossover
    #for individual in population:
    #    new_population.append(individual)
    
    return new_population


def select(pool, fits):
    if Params.selectMethod == "Tournament":
        return selectByUnreal(pool, fits, Params.poolSize, Params.tournmntSize)

    else:
        raise Exception("Unknown selection method: {}!"
                .format(Params.selectMethod))



def initPool(N):
    pool = []
    for _ in xrange(N):
        pool.append(Genotype())

    return pool 

def costToFits(costs):
    m = max(costs)
    return [(float(m)-c)/m for c in costs]
    
def rule15(success, fail):
    
    ratio = float(success)/(fail+success)
    
    #print ratio
    
    if ratio > Params.mutation15Thresh and Params.mutationProb>0.05:
        Params.mutationProb = Params.mutationProb - 0.01
        #print('decreased mutationProb to {}'. format(Params.mutationProb))
    elif ratio < Params.mutation15Thresh and Params.mutationProb<1.0:
        Params.mutationProb = Params.mutationProb + 0.01
        #print('increased mutationProb to {}'. format(Params.mutationProb))
        
def simulate():
    pool = initPool(Params.poolSize)
    bestSoFar = 999999999999999999
    success = 0
    fail = 0
    
    for simStep in xrange(Params.simSteps):
        
        if simStep != 0 and simStep%Params.generations15==0:
            #print('success {} - fail {}'. format(success, fail))
            rule15(success, fail)
            success = 0
            fail = 0
            
        bestInStep = 99999999999999999999

        fitnessV = []
        for gType in pool:
            fitness = gType.getFitness()
            fitnessV.append(fitness)

            if fitness < bestSoFar:
                bestSoFar = fitness
                #print('New best genotype found: {} -> {}'.
                #        format(gType.getGenoType(), fitness))

            if fitness < bestInStep:
                bestInStep = fitness

        print bestSoFar
        #print('{}: bestInStep: {}, bestSoFar: {}'.format(simStep, bestInStep,
        #    bestSoFar))

        # Selekcja osobników do krzyżowania
        mate_pool = select(pool, costToFits(fitnessV))
        pool = []

        # Krzyżowanie
        for _ in xrange(Params.poolSize):
            spec1 = random.choice(mate_pool)
            spec2 = random.choice(mate_pool)
            pool.append(spec1.crossOver(spec2))
            pool.append(spec2.crossOver(spec1))

        # Mutacje
        for gType in pool:
            if random.random() < Params.mutationProb:
                oldFitness=gType.getFitness()
                gType.mutate()
                if gType.getFitness() > oldFitness:
                	fail=fail + 1
                else:
                	success= success + 1


#def main():
    #euclidParse("111Eucl.txt")
    #simulate()

    #g = Genotype()
    #for _ in xrange(5):
    #    g.getFitness()
    #    g.mutate()

    #gen1=Genotype([10, 12,13,16,18,19,23])
    #gen2=Genotype([5,10])
    
    #print gen1.getGenoType()
    #newGen = gen1.crossOverOnePoint(gen2).getGenoType()
    
    #print newGen
#if __name__ == '__main__':
#    main()

