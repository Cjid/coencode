import os
import pandas

"""
Created by Coen Neijssel
Credits to Jim Barrett's postprocessing.py from 
which I stole the loop for going through directories :D

Currently the folders are named in the following way,

mass_metallicity
Example:
50.0_0.0001    

To get the data you past lists of mass, metallicity and files
At the moment you cannot get multiple types of files yet [TODO]


example  retrieve_data([50.0], [0.0001], ['dataOutput_0.dat'])
if you want all metallicities for a given mass;
example  retrieve_data([50.0], ['All'], ['dataOutput_0.dat'])

Returns the concatenated (all in one) PANDAS_dataframe



EXTRA Note;
At this moment (30-May-2017)
The detailed output also contains a column with M1ZAMS, M2ZAMS, and separation_initial
This has not been pushed yet
"""

def retrieveData(requestedMasses=None, requestedMetallicities=None, whichFile=['dataOutput_0.dat'],\
                 absolutePathToSSEGrid='/home/cneijssel/Documents/Projects/Data/SSE_grid_folders/'):


    if not isinstance(requestedMasses, list):
        raise TypeError("Masses should be passed as a list (even single one)")

    if not isinstance(requestedMetallicities, list):
        raise TypeError("Metallicities should be passed as a list (even single one)")

    if not isinstance(whichFile, list):
        raise TypeError("file names be passed as a list (even single one)")


    counter = 0
    data = None

    for r,dirs,f in os.walk(absolutePathToSSEGrid):

        for d in dirs:
            mass, metallicity = d.split('_')

            retrieveSwitch1 = False
            if (float(mass) in requestedMasses) or (requestedMasses[0]=='All'):
                retrieveSwitch1 = True
            retrieveSwitch2 = False
            if (float(metallicity) in requestedMetallicities) or (requestedMetallicities[0]=='All'):
                retrieveSwitch2 = True

            if (retrieveSwitch1 and  retrieveSwitch2):
                df = pandas.read_table(absolutePathToSSEGrid+str(d)+'/'+whichFile[0],\
                                       header=1, delim_whitespace=True)
                if counter ==0:
                    data = df.copy()
                else:        
                    data = pandas.concat([data,df], ignore_index = True)
                counter+=1

    print 'Nr files/stars combined =' , counter
    return data





