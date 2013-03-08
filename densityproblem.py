'''
Created on Dec 17, 2012

@author: ivihernandez
'''

#ivan's imports
import facilitylocationproblem
import myutils
import candidatelist
#standard imports
import time
import os
import sys
import random
import copy
#other libraries
import inspyred

from inspyred.ec import emo



class DensityProblem(facilitylocationproblem.UncapacitatedFacilityLocationProblem):
    def __init__(self,
                 originalProblem,
                 paretoSolutions,
                 resultsFolder):
        self.objectiveTypes = originalProblem.get_objective_functions_types()
        self.objectiveFunctions = originalProblem.get_objective_functions()
        self.bounder = inspyred.ec.Bounder(0, 1)
        
        self.distribution = originalProblem.distribution
        self.demand = originalProblem.demand
        self.prng = originalProblem.prng
        self.maximize = True
        self.debug = False
        self.evaluations = 0 #counter for the number of evaluations performed
        self.capacitated = originalProblem.capacitated #capacitated or uncapacitated case?
        self.weighted = originalProblem.weighted #capacitated or uncapacitated case?
        self.minDistance = None #minimum of all the minimum distances
        self.maxDistance = None #maximum of all the minimum distances
        self.show = False #do not show the figures while running
        self.myformat = "pdf"
        self.chromosomeType = None
        
        
        self.dimensions = len(self.distribution)#self.distribution.number_of_nodes()
        
        self.oldArchive = paretoSolutions
        self.resultsFolder = resultsFolder
        
        
    def extend_pareto(self, r=1, s=10000, myrange=(1, 50)):
        """
            explore more the pareto archive, for a given r
            @param r: only consider designs with # of failures =r
            @param s: size of the sample to create for each element of the
            original pareto  
        """
        
        interdictedName = "get_interdicted_facilities"
        indexOfInterdictedFacilities = None
        
        for myindex, name in enumerate(self.objectiveFunctions):
            if (interdictedName == name):
                indexOfInterdictedFacilities = myindex
                break
        self.population = []
        
        
        objectiveTypes = self.objectiveTypes
        total = len(self.oldArchive)
        print "old archive",total
        
        for index, f in enumerate(self.oldArchive):
            zeros = f.candidate.count(0)
            if zeros == len(f.candidate):
                continue
            getOut = False
            for fit in f.fitness:
                if fit >= sys.maxint:
                    getOut = True
                    break
            if getOut:
                continue
            
            #temporary watch out, this is for interdiction
            if indexOfInterdictedFacilities != None:
                if f.fitness[indexOfInterdictedFacilities] != r:
                    continue
            
            p = len(f.candidate) - zeros
            cand = [1]*p + [0]*zeros
            (lower, upper) = myrange
            if p <= lower or p >= upper:
                getOut = True
                continue
            
            
            
            #add the original candidate
            self.population.append(f)
            lowerBound = f.fitness.values[1]
            upperBound = f.fitness.values[2]
            ###############################
            #try to find k different solutions with the same p, 
            #and put them in a set W
            k = p
            
            W = set()
            for i in range(k):
                random.shuffle(cand)
                if cand == f.candidate:
                    continue
                W.add(tuple(cand))
            
            
            
            for cand in W:
                cand = list(cand)
                worstFitness = 0
                for i in range(s):
                    shutdownIndex = [i for i,_ in enumerate(cand) if cand[i]==1]
                    toShut = random.sample(shutdownIndex, r)
                    
                    failedCand = copy.deepcopy(cand)
                    for j in toShut:
                        failedCand[j] = 0
                    
                    for name in self.objectiveFunctions:
                        if name == "get_total_distance_after_interdiction":
                            beforeDistance = self.get_total_distance(cand)
                            afterDistance = self.get_total_distance(failedCand)
                        
                    
                    values = []
                    #hardwired
                    values.append(p)
                    values.append(beforeDistance)
                    values.append(afterDistance)
                    values.append(int(r))
                    
                    
                    fit = emo.Pareto(values, objectiveTypes)
                    cand = candidatelist.Candidatelist(cand)
                    cand.set_map(self.map)
                    ind = inspyred.ec.Individual(copy.deepcopy(cand))
                    ind.fitness = fit
                    if afterDistance < upperBound:
                        
                        self.population.append(ind)
                    
                    
            
            
            
        
        self.newArchive = []
        
        
        self.archiver = inspyred.ec.archivers.best_archiver
        self.newArchive = self.archiver(random=self.prng, population=list(self.population), archive=list(self.newArchive), args=None)
        
        
        ea = emo.NSGA2(self.prng)
        ea.__class__.__name__ = "MOPSDA & NSGA2"
        ea.archive = self.newArchive
        ea.archive.sort(cmp=myutils.individual_compare)
        
        return self.newArchive
              
                
    def generator(self, random, args):
        retval = [random.choice([0, 1]) for _ in xrange(self.dimensions )]
        return candidatelist.Candidatelist(retval)
        #return retval
