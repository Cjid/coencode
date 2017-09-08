import numpy
import pandas

class TagEventsInDataFrame(object):
    

    def __init__(self, events=['GW150914', 'GW151226', 'LVT151012','GW170104'],\
                       cropCompleteFrame=True, M1isHeaviest=False):
        self.events = events
        self.cropCompleteFrame = cropCompleteFrame
        self.M1isHeaviest = M1isHeaviest
        



    def eventInformationDataframe(self):
        """Creates a dataframe with the selection criteria of the events
           References Abott et al. 2016 (O1 BBH paper) and Abott et al. 2017 (GW170104)
           TODO add arXiv numbers

           ul= upperlimit, ll=lowerlimit, use_total_mass=1 means Mtot more constraining than MChirp

           The colours are the hexidecimal colours used by LIGO plots
        """
    
        eventNames =['GW150914', 'GW151226', 'LVT151012','GW170104']
        columns = ['eventName', 'chirp_mass', 'chirp_ul', 'chirp_ll', 'total_mass', 'tot_ul', \
                    'tot_ll', 'lower_q', 'use_total_mass', 'eventNr', 'colour']
        index = range(len(eventNames))
        dfEvents = pandas.DataFrame(index=index, columns=columns)

                           #Name       chirp +   -    Mtot  +    -    q (90%)  UseMtot  Assign Nr  colour
        dfEvents.loc[0] = ['GW150914',  28.1 ,1.8,-1.5, 65.3,3.8 ,-3.4, 0.65,    1,       1,    '#0072b2']
        dfEvents.loc[1] = ['LVT151012', 15.1 ,1.4,-1.1, 37.0,13.0,-4.0, 0.24,    0,       2,    '#009e73']
        dfEvents.loc[2] = ['GW151226',  8.9  ,0.3,-0.3, 21.8,5.9 ,-1.7, 0.28,    0,       3,    '#d55e00']
        dfEvents.loc[3] = ['GW170104',  21.1 ,2.4,-2.7, 50.7,5.7 ,-4.6, 0.46,    1,       4,    '#cc79a7']


        return dfEvents



    def chirpMassRatioTotalMass(self, dataFrame):

        dataFrame['q'] = 1.0                   #create the column mass ratio
        idx  = dataFrame['M2']>dataFrame['M1'] #indices where M2 heavier M2 is denominator
        dataFrame.loc[idx,['q']] = dataFrame.loc[idx,['M1']].values/dataFrame.loc[idx,['M2']].values
        idx2 = numpy.invert(idx) #everywhere where the logical invert is true M1 is denominator
        dataFrame.loc[idx2,['q']] = dataFrame.loc[idx2,['M2']].values/dataFrame.loc[idx2,['M1']].values


        if self.M1isHeaviest:
            dataFrame.loc[idx,['M1','M2']] = dataFrame.loc[idx,['M2','M1']].values

        dataFrame['chirpMass'] = (dataFrame['M1']+dataFrame['M2'])* (dataFrame['q']**(3.0/5.0))\
					            *((1.0+dataFrame['q'])**(-6.0/5.0))


        dataFrame['Mtot'] = dataFrame['M1'] + dataFrame['M2']
        return dataFrame




    def tagBinariesWithEvent(self, dataFrame):
        """Given the dataFrame and the events of interest it will add the following columns:

            chirpMass - Msun 
            q(ratio)  - lighter/heavier
            Mtot      - Msun
                        Above are all done in chirpMassRatioTotalMass()

            eventName - if not an event set to 'notAnEvent'
            colour    - the hexidecimal (?check) colour used by LIGO
                        set to white #FFFFFF if notAnEvent
        """
        if dataFrame.empty:
            raise ValueError('input dataFrame is empty!')
    
        dataFrame = self.chirpMassRatioTotalMass(dataFrame)
        eventInfo = self.eventInformationDataframe()

        dataFrame['eventName'] = 'notAnEvent'
        dataFrame['colour']    = '#FFFFFF'

        for nr, eventName in enumerate(self.events):

            criteria = eventInfo.loc[eventInfo['eventName']==eventName]
            if criteria['use_total_mass'].item()==1:
                MtotUpper = criteria['total_mass'].item() + criteria['tot_ul'].item()
                MtotLower = criteria['total_mass'].item() + criteria['tot_ll'].item()
                BooleanTotMass=  (MtotLower < dataFrame['Mtot']) &(dataFrame['Mtot']<MtotUpper)
                BooleanRatio = criteria['lower_q'].item() < dataFrame['q']
                Booleans = BooleanTotMass & BooleanRatio
                dataFrame.loc[Booleans,['eventName']] = eventName
                dataFrame.loc[Booleans,['colour']]    = criteria['colour'].item()

            else:
                MChirpUpper = criteria[ 'chirp_mass'].item() + criteria['chirp_ul'].item()
                MChirpLower = criteria[ 'chirp_mass'].item() + criteria['chirp_ll'].item()
                BooleanChirpMass=  (MChirpLower < dataFrame['chirpMass']) &(dataFrame['chirpMass']<MChirpUpper)
                BooleanRatio = criteria['lower_q'].item() < dataFrame['q']
                Booleans = BooleanChirpMass & BooleanRatio
                dataFrame.loc[Booleans,['eventName']] = eventName
                dataFrame.loc[Booleans,['colour']]    = criteria['colour'].item()


        #If you want only the data that is labeled as an event.
        print len(dataFrame)
        if self.cropCompleteFrame:
            print 'doing this'
            dataFrame = dataFrame[dataFrame['eventName'] != 'notAnEvent']
        print len(dataFrame)

        if dataFrame.empty:
            raise ValueError('output dataFrame is empty!')

        return dataFrame




"""
Hack for contourPlot confidence interval Masses this only for mirrorFlipped
see if y>x pass statement


def chirpmass(x,y):
    Mc = ((x*y)**(3.0/5.0)) / ((x+y)**(1.0/5.0))
    return Mc


def criteriaLVT151012(Mc,q):
    if (Mc>14.0)&(Mc<16.5)&(q>0.24):
        return 1
    else:
        return 0


def criteriaGW151226(Mc,q):
    if (Mc>8.6)&(Mc<9.2)&(q>0.28):
        return 1
    else:
        return 0

def criteriaGW150914(Mtot, q):
    if (Mtot>61.9)&(Mtot<69.1)&(q>0.65):
        return 1
    else:
        return 0


def criteriaGW170104(Mtot, q):
    if (Mtot>46.1)&(Mtot<56.4)&(q>0.46):
        return 1
    else:
        return 0

xs = numpy.linspace(0,50,1000)
ys = numpy.linspace(0,50,1000)[::-1]

X,Y= numpy.meshgrid(xs,ys)

LVT151012array = numpy.zeros(shape=(len(xs), len(ys)))
GW151226array =  numpy.zeros(shape=(len(xs), len(ys)))
GW150914array = numpy.zeros(shape=(len(xs), len(ys)))
GW170104array = numpy.zeros(shape=(len(xs), len(ys)))
for nrx, x in enumerate(xs):
    for nry, y in enumerate(ys):

        
        if y>x:
            pass

        if y<x:
            Mc = chirpmass(x,y)
            ratio = y/float(x)
            Mtot = x+y
            LVT151012 = criteriaLVT151012(Mc,ratio)
            GW151226  = criteriaGW151226(Mc,ratio)
            GW150914  = criteriaGW150914(Mtot, ratio)
            GW170104  = criteriaGW170104(Mtot, ratio)
            if LVT151012 ==1:
                LVT151012array[nry][nrx] = 1
            if GW151226 ==1:
                GW151226array[nry][nrx] = 1
            if GW150914 ==1:
                GW150914array[nry][nrx]=1   
            if GW170104 ==1:
                GW170104array[nry][nrx]=1



axes.contour(X,Y, LVT151012array,[0],  colors=('#009e73'), linestyles='--', linewidths=5.0)
axes.contour(X,Y, GW151226array,[0],   colors=('#d55e00'), linestyles='--', linewidths=5.0)
axes.contour(X,Y, GW150914array,[0],   colors=('#0072b2'), linestyles='--', linewidths=5.0)
axes.contour(X,Y, GW170104array,[0],   colors=('#cc79a7'), linestyles='--', linewidths=5.0)
"""
