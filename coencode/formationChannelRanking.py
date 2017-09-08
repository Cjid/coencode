import pandas
import numpy


class rankChannels(object):


    def __init__(self,dataFrame, verbose=True, selectColumns=None, dropColumns=None):

        self.verbose = verbose

        self.columnsOfInterest = self.reduceColumnsOfInterest(dataFrame, selectColumns, dropColumns)

        if verbose:
            self.printHeaderFormationChannels(dataFrame)
        return



    def reduceColumnsOfInterest(self, dataFrame, selectColumns, dropColumns):
        """Creates a list of columns we are interested in to differentiate between formation
           channels. 
        """
        allPossible = list(dataFrame.columns)
        allPossible.remove('m_randomSeed') #different channels never depend no Seed
        allPossible.remove('eventCounter') #never sensible to select on TODO remove(?)

        if (selectColumns is None)&(dropColumns is None):
            listSelectedColumns = allPossible

        if (isinstance(selectColumns, list))&(isinstance(dropColumns, list)):
            raise ValueError("\ncannot select AND drop columns, set either of them to None")

        if (not ((isinstance(selectColumns, list) or (selectColumns is None))) or 
            not ((isinstance(dropColumns, list) or (dropColumns is None)))):
            raise TypeError("\n arguments selectColumns/dropColumns should be either list or None type")

        if isinstance(selectColumns, list):
            listSelectedColumns = selectColumns

        if isinstance(dropColumns, list):
            for dropName in dropColumns:
                allPossible.remove(dropName)
            listSelectedColumns = allPossible

        return listSelectedColumns



    def printHeaderFormationChannels(self, dataFrame):
            columns = list(dataFrame.columns)
            columns.remove('m_randomSeed')
            columns.remove('eventCounter')
            print(columns)

    def verboseMessage(self,Message):
        if self.verbose:
            print(Message)

    def returnFrameUniqueSortedChannels(self, dataFrame):
        """Returns an array with the unique arrays of formation channels only looking at
           the columns of interest. The arrays are in ascending order. However, even if you only
           selected one column to look at, you might get more than two channels. Because
           if things happened in a different order the number entry in the same column will be
           different. TODO rewrite explanation
        """

        self.verboseMessage("creating 2D array unique sorted channels")
        dfGroup = dataFrame.copy()
        # Group the dataFrame using only the columns of interest
        dfGroup = dfGroup.groupby(self.columnsOfInterest)
        #Collapse the group, reset the index and create a Column with the number of occurences
        #of each Channel. (not legible sorry).
        dfCount = pandas.DataFrame(dfGroup.size().reset_index(name = "ChannelCount"))
        #Ranking the channels highest count is first row NO DUPLICATES
        dfChannelsRanked = dfCount.sort_values(['ChannelCount'], ascending=0).copy()
        #Create a column with the rank number
        dfChannelsRanked['rank']=numpy.array(range(1,len(dfChannelsRanked)+1))       
        return dfChannelsRanked



    def returnArrayWithRank(self, dataFrame):
        """Uses a for loop over dataFrame to look up each row in
           the sortedUniqueChannels and label it with its corresponding rank
        """


        sortedUniqueChannels = self.returnFrameUniqueSortedChannels(dataFrame)

        self.verboseMessage("Returning array (len(data)) with rank each system\n Could take long :s")
        dfCounts = dataFrame.copy()
        dfCounts['rank'] = dfCounts['eventCounter'].copy() #creat a column for use later

        #Again we have to ignore the columns we are not interested in however we do want the rank.
        maskedOriginalFrame = dfCounts[self.columnsOfInterest].copy()
        maskedSortedFrame = sortedUniqueChannels[self.columnsOfInterest].copy()

        #For each row in dataFrame look up the similar line in sortedChannels
        #and write down its rank. Sadly we cannot use a dictionary between counts and rank
        #since there might be degenerate key values.
        for row, line in maskedOriginalFrame.iterrows():
            l = line.as_matrix()
            positionInSorted = numpy.where((maskedSortedFrame == l).all(axis=1))[0][0]
            dfCounts.loc[row]['rank'] = sortedUniqueChannels.iloc[positionInSorted]['rank']

        return dfCounts








    
