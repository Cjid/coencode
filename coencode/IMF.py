import numpy as np
import matplotlib.pyplot as plot



def powerlaw(m):
    pdf = np.ones(len(m))

    xmin1 = 0.01
    alpha1 = 0.3
    C1 = (1.0/(xmin1**(-alpha1)))    


    xmin2 = 0.08
    alpha2 = 1.3
    C2  = (1.0/(xmin2**(-alpha2)))
    Cconnecto1 = ((xmin2**(-alpha1))) * C1
    C2 = C2*Cconnecto1

    xmin3 = 0.5
    alpha3 = 2.3
    C3 = (1.0/(xmin3**(-alpha3)))
    Cconnecto2 = ((xmin3**(-alpha2))) * C2
    C3 = C3 * Cconnecto2

    mask1 = m<xmin2
    pdf[mask1]=C1 * (m[mask1]**(-alpha1))

    mask2 = (m<xmin3) & (m>xmin2)
    pdf[mask2]=C2 * (m[mask2]**(-alpha2))
    
    mask3 = (m>=xmin3) 
    pdf[mask3]=C3 * (m[mask3]**(-alpha3))

    return pdf

    
def uniformInRange(lower,upper,size=None):

    return (upper-lower)*np.random.rand(size) + lower
    


def createSampleUniverse(sampleSizeUniverse, pathToSampleUniverse,verbose=False):
    
    nSystems = sampleSizeUniverse
    batchSize = 100000

    #how often to print progress in verbose mode (e.g 10 = every 10%), and a variable to keep
    #track of how far we are
    percentageSpacing = 10
    percentageCounter = percentageSpacing
    binaryFraction    = 0.7
    formedSystems = []

    while len(formedSystems) < nSystems:

        #primary masses  carefull if you change lower boundary some normalizations change.
        #m1s = uniformInRange(0.01,200,size=batchSize)   
        m1s = np.random.uniform(0.01, 200, size=batchSize)
        #rejection sampling probs
        ps = np.random.rand(batchSize)
        
        #boolean mask of where things formed
        formedMask = ps < powerlaw(m1s)
        
        #more rejection sampling probs
        ps = np.random.rand(batchSize)
        
        #where did we form binaries
        binaryMask = ps < binaryFraction
        
        #mass ratios
        ratios = uniformInRange(0.1,1.,size=batchSize)
        
        #even more rejection sampling probs
        ps = np.random.rand(batchSize)
        
        #the secondary masses (default is zero)
        m2s = np.zeros(batchSize)
        
        #where we formed binaries, calculate mass
        m2s[binaryMask] = m1s[binaryMask] * ratios[binaryMask]
        
        thisBatch = np.column_stack((m1s,m2s))[formedMask]
        formedSystems.extend(list(thisBatch))

        if verbose:

            percentageDone = (100*len(formedSystems))/nSystems

            if percentageDone > percentageCounter:

                print "successfully generated " + str(percentageCounter) + r"% of systems"
                percentageCounter += percentageSpacing
        
    #we don't care that we may have a few too many systems
    np.savetxt(pathToSampleUniverse,formedSystems, header='mass1\tmass2', comments='')


createSampleUniverse(5e6, './sample70',verbose=True)

