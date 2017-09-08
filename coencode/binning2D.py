import numpy     #for handling arrays
import pandas    #for handling data

"""
Created by Coen Neijssel during master thesis :D Winter 2015
Thourough clean up/spring cleaning and OOP!!!! during 1st year PhD on 30-31 May-2017

The goal is 2D binning, useful for imshow or colourcoded histograms
The default is set to give you the delay time distribution of your dataframe (or it will break :p)
"""
class binning2D(object):

    def __init__(self, verbose=True, binningY=False, weightedHist=False, nameColumnWeights='weights', \
                 normalizePerBinWidthX =True, normalizeTotalNumber = False,\
                 nameColumnBinsX='tc', minValueX=0.01, maxValueX=15e4,  nrBinsX=200, logBinningX=True,\
                 nameColumnBinsY='tc', minValueY=0.01, maxValueY=15e4,  nrBinsY=10, logBinningY=True):


        """ General settings for Binning
        """
        self.verbose   = verbose
        self.binningY  = binningY

        self.weightedHist     = weightedHist
        self.nameColumnWeights= nameColumnWeights
        
        self.normalizePerBinWidthX    = normalizePerBinWidthX
        self.normalizeTotalNumber     = normalizeTotalNumber      
    
        """ Settings  bins X-axis direction
        """
        self.nameColumnBinsX = nameColumnBinsX
        self.minValueX       = minValueX
        self.maxValueX       = maxValueX
        self.nrBinsX         = nrBinsX
        self.logBinningX     = logBinningX
        self.edgesX, self.binWidthsX = self.createBins(self.logBinningX, self.minValueX,\
                                                       self.maxValueX, self.nrBinsX)

        """ Settings  bins Y-axis direction
        """
        self.nameColumnBinsY = nameColumnBinsY
        self.minValueY       = minValueY
        self.maxValueY       = maxValueY
        self.nrBinsY         = nrBinsY
        self.logBinningY     = logBinningY
        self.edgesY, self.binWidthsY = self.createBins(self.logBinningY, self.minValueY,\
                                                       self.maxValueY, self.nrBinsY)

        self.verbosePrintOptions()

    def createBins(self,logBinning, minValue, maxValue, nrBins):
        if logBinning:
            minValue = numpy.log10(minValue)
            maxValue = numpy.log10(maxValue)
            edges    = numpy.logspace(minValue, maxValue, nrBins+1, base =10.0)
        else:
            edges    = numpy.linspace(minValue, maxValue, nrBins+1)

        binWidths = (edges[1:] - edges[:-1])

        return edges, binWidths









    def binningX(self, data):

        nrLines  = len(data)
        array2D = numpy.zeros(shape=(self.nrBinsX, nrLines), dtype=bool)
        
        """ Bin the data and change the above Boolean accoringly if the line falls in a bin
            then that bin is assigned true. Basically I am binning lines not data, this is important
            since this means that all the information in each line is maintained. 
        """
        dataX = data[self.nameColumnBinsX].as_matrix()
       
        for i in range(len(self.edgesX)-1): #-1 because last edge does not relate to a bin
            array2D[i] = (dataX  <= self.edgesX[i+1] ) & (dataX > self.edgesX[i])

        """"This array now looks like

                       line 1   line 2  line 3  line 4   .... len(data)
                       ---------------------------------------------
            bin  1   |  False   True    False  False              |    <---
            bin  2   |  True    False   False  False              |       |
            bin  3   |  False   False   True   False              |       |
              .      |                                ..          |       |
              .      |                                  ..        |       | 
            nr_bins_h|                                            |       |
                     -----------------------------------------------      |
                                                                          |
                                                                          |
                This sum is total value in bin1 since True reads as 1 in numpy.sum()


             You could either sum only the True to see the  number of systems in each bin 
            (e.g. no weights) or you could multiply each element with its weight.

        """

        return array2D


    def binningYFunc(self, array, data):
        nrLines  = len(data)
        dataY    = data[self.nameColumnBinsY].as_matrix()
        array3D = numpy.zeros(shape=(self.nrBinsX, self.nrBinsY, nrLines), dtype=bool)
        for nr, line in enumerate(array):          #for every bin
            dat = line * dataY                          #looks if the line is in that bin since line is 
                                                      #True or False. If True then value continues for
                                                      # binning. If false then value is zero and will
                                                      # fall outside of bins.
            for j in range(len(self.edgesY)-1):           #bin them again with booleans
               array3D[nr][j] = (dat <= self.edgesY[j+1] ) & (dat > self.edgesY[j])
        return array3D

    def weightArray(self, array, data):
        weightedArray = numpy.zeros(shape=array.shape)
        if self.weightedHist:
            if self.binningY:
                weights = data[self.nameColumnWeights].as_matrix()
                print numpy.sum(weights)
                xs, ys, zs = array.shape
                for x in range(xs):
                    for y in range(ys):
                        weightedArray[(x,y)] = numpy.multiply(array[(x,y)],  weights)
                array = weightedArray
            else:
                weights = data[self.nameColumnWeights].as_matrix()
                weightedArray = numpy.multiply(array, weights)
                array = weightedArray
        return array



    def normalizeBins(self, array):
        if self.normalizePerBinWidthX:
            array = array/self.binWidthsX
        if self.normalizeTotalNumber:
            array = array/float(numpy.sum(array) )
        return array


    def collapseTransposeArray(self, array):
        if self.binningY:
            array = numpy.sum(array, axis =2)
        else:
            array = numpy.sum(array, axis =1)

        #row is now a bin so Transpose that each column is a bin
        array = array.T
        return array


    def mainFunction(self, data):

        array = self.binningX(data)

        if self.binningY:
            array = self.binningYFunc(array, data)

        array = self.weightArray(array, data)
        array = self.collapseTransposeArray(array)
        array = self.normalizeBins(array)
        return array, self.edgesX, self.edgesY

    def verbosePrintOptions(self):
        if self.verbose:
            verboseText ='''\n \n            2D-Binning created by Coen Neijssel :D
                           \r         Options for settings and their default values\n
                           \r--------------------------------------------------------------
                           \r|                                                            |
                           \r|  verbose=True                 binningY=False               |
                           \r|  weightedHist=False           nameColumnWeights='weights'  |
                           \r|  normalizePerBinWidthX =True  normalizeTotalNumber = False |
                           \r|  nameColumnBinsX='tc'         minValueX=0.01               |
                           \r|  maxValueX=15e4               nrBinsX=200                  |
                           \r|  logBinningX=True             nameColumnBinsY='tc'         |
                           \r|  minValueY=0.01               maxValueY=15e4,              |
                           \r|  nrBinsY=10                   logBinningY=True             |
                           \r|                                                            |
                           \r--------------------------------------------------------------
                        '''
            print verboseText  #used \r to not print indentation




