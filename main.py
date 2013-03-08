'''
Created on Aug 16, 2012

@author: ivihernandez
'''
"""
    This program takes as input a Pareto set of :
    minimize: distance (prior to failure) (lower bound)
    minimize: number of facilities
    minimize: number of facilities that fail
    maximize: distance (after failure) (upper  bound)
    
    and finds multiple solution within the lower and upper bounds
"""
#standard imports
import time
import os
import random
#non standard import

#ivan's import
import parameterreader
import myutils
import facilitylocationproblem
import densityproblem

def density_estimator(experimentFile,
                      paretoFile,
                      numberOfFailures,
                      numberOfSimulations,
                      facilitiesRange): 
    """
         Determine how many elements there are in the threshold
         of the Pareto set between LowerBound and UpperBound.
         Where LowerBound is the Distance and UpperBound is the
         distance after failure. Solutions within the bound are of 
         interest to the decison maker, they extend the Pareto in a useful
         way. Outside the threshold solutions are not Pareto Optimal, or if they
         are, they are of no interest.
    """
    
    prng = random.Random()
    #myseed = time.time()
    myseed = 34525432
    prng.seed(myseed)
     
    inputFolder = "inputs"
    resultsFolder = 'density results '
    mydate = time.strftime("%a %d %b %Y %H %M %S", time.gmtime())
    resultsFolder += mydate
    
    
    
    parameterReader = parameterreader.ParameterReader(experimentFile)
    parameterReader.show()
    distributionCenters = os.path.join(inputFolder, parameterReader.datasetFiles[0])
    demandCenters = os.path.join(inputFolder, parameterReader.datasetFiles[1])
    
    args = [distributionCenters, demandCenters]
    originalProblem = facilitylocationproblem.UncapacitatedFacilityLocationProblem(args, prng, parameterReader, resultsFolder,"PSDA & NSGA-II")
    
    
    
    paretoSolutions = myutils.load_pareto(paretoFile)
    
    try:
        os.mkdir(resultsFolder)
    except:
        pass
    densityProblem = densityproblem.DensityProblem(originalProblem, 
                                                   paretoSolutions, 
                                                   resultsFolder)
    start = time.clock()
    sol = densityProblem.extend_pareto(r=numberOfFailures,
                                       s=numberOfSimulations,
                                       myrange=facilitiesRange)
    
    end = time.clock()
    diff = (end-start)/60.0
    attributes = {}
    attributes["time"] = diff
    additionalAttributes = {}
    additionalAttributes["seed"] = myseed
    outputFilePath = os.path.join(resultsFolder, "ordinal-optimization.xml")
    myutils.log_solution(outputFilePath, 
                         sol, 
                         "ordinal optimization", 
                         originalProblem.get_objective_functions(), 
                         originalProblem.get_objective_functions_types(), 
                         attributes, 
                         additionalAttributes
                         )
    

if __name__ == '__main__':
    print 'Program started'
    densityEstimator = False
    start = time.clock()
    
    numberOfFailures = 1
    numberOfSimulations = 1000
    facilitiesRange = (2, 8)
    experimentFile = r'..\facility-location\src\results Thu 07 Mar 2013 20 03 35\a-experiment-swain-total-distance-interdiction.xml'
    paretoFile = r'..\facility-location\src\results Thu 07 Mar 2013 20 03 35\combined-pareto-2.xml'
    
    density_estimator(experimentFile, 
                      paretoFile, 
                      numberOfFailures,
                      numberOfSimulations,
                      facilitiesRange)
    
    end = time.clock()
    print 'Program finished in ',(end-start)/60.0 ,' minutes'