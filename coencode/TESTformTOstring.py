import pandas
import numpy

def linker(number, star):

    stellar_types = {0:'MS<0 ',1:'MS ', 2:'HG ', 3:'FGB ', 4:'CHeB ', 5:'EAGB ', 6:'TPAGB ',\
         7:'HeMS ',8:'HeHG ',9:'HeGB ', 10:'HeWD ', 11:'COWD ', 12:'ONeWD ',\
         13:'NS ', 14:'BH ', 15:'MR '}

    started_by ={0:'primary',1:'secondary',2:'both'}
    boolean = {0:'False', 1:'True'}

    string_return = ''
    if number==0:
        string_return +=''#'Started by=%s'%(started_by[star]) 
    if number==1:
        string_return +='P=%s'%(stellar_types[star]) 
    if number==2:
        string_return +='S=%s'%(stellar_types[star]) 
    if number==3:
        string_return += boolean[star]
    if number==4:
        string_return += ''
    return string_return

    


def formation_to_string(Selectby, line):
    Count = line['ChannelCount']
    rank  = line['rank']
    outputstring = 'rank/count='+str(rank)+'/'+str(line['ChannelCount'])+':\n'
    
    #The channels might be ranked by specific columns
    #Therefore we cannot convert to string based on all columns
    #only the ones at our disposal which are
    Columns = Selectby


    #Not every column relates to the order of events, some
    # are extra info such as the stellar types during a MT episode
    #If we sort our columns on chronological order these numbers should not be involved
    #Made it a dictionary to link it to the column its info corresponds to
    #Probably a better way to keep it al felxible but couldn't think of one TODO
    Extra_info = {'mt_primary_ep1_K1':('mt_primary_ep1', 1),
                  'mt_primary_ep1_K2':('mt_primary_ep1', 2),
                  'mt_primary_ep2_K1':('mt_primary_ep2', 1),
                  'mt_primary_ep2_K2':('mt_primary_ep2', 2),
                  'mt_primary_ep3_K1':('mt_primary_ep3', 1),
                  'mt_primary_ep3_K2':('mt_primary_ep3', 2),
                     'mt_secondary_ep1_K1':('mt_secondary_ep1',1),
                  'mt_secondary_ep1_K2':('mt_secondary_ep1',2),
                  'mt_secondary_ep2_K1':('mt_secondary_ep2',1),
                  'mt_secondary_ep2_K2':('mt_secondary_ep2',2),
                  'mt_secondary_ep3_K1':('mt_secondary_ep3',2),
                  'mt_secondary_ep3_K2':('mt_secondary_ep3',2),
                  'CEE_instigator':('CEE',0),'CEE_failed_instigator':('CEE_failed',0),
                  'CEE_wet_instigator':('CEE_wet',0)}#,'stellar_type_K1':('stellar_type_K1',0), 
                  # 'stellar_type_K2':('stellar_type_K2',0),
                #  'merged_in_Hubble_time':('merged_in_Hubble_time',0),
                #  'Channel_Count':('Channel_Count',0)}

    Changed_name = {'mt_primary_ep1':'mt_primary_ep1','mt_primary_ep2':'mt_primary_ep2',
                    'mt_primary_ep3':'mt_primary_ep3','mt_secondary_ep1':'mt_secondary_ep1',
                    'mt_secondary_ep2':'mt_secondary_ep2','mt_secondary_ep3':'mt_secondary_ep3',
                    'CEE':'CEE','CEE_failed':'CEE_failed','CEE_wet':'CEE_wet'}


    Append_info_end ={'stellar_type_K1':(' final type Primary=',1) ,
                      'stellar_type_K2':('  final type Secondary=' ,2),
                      'merged_in_Hubble_time': ('  merged in Hubble_time=',3),
                      'binary_disbound': ('  binary disbound=', 3),
                      'ChannelCount':('ChannelCount',0),
                      'rank':('rank',4)}



    for info in list(Extra_info.keys()):
        if info in Columns:
            star = line[info]
            name_to_replace = Extra_info[info][0]
            new_name = linker(Extra_info[info][1], star)
            
            Changed_name[name_to_replace] +=' '+new_name

    for name in list(Changed_name.keys()):
        if name in Columns:
            line = line.rename({name: Changed_name[name]})

    #However if we have a masstransfer event for which we select
    # AND we do want this info we need to look up this info





    dfChronos = line.copy()
    for name in list(Extra_info.keys()):
        try:
            dfChronos = dfChronos.drop(name)
        except:
            pass #didnt have this column in Selectby (see main)

    #everything that is zero didn't happen so drop it
    dfChronos = dfChronos[(dfChronos!=0)]
    #now sort them in chronological order
    dfChronos = dfChronos.sort_values(axis=0, ascending=True)


    sort_columns=dfChronos.index.tolist()
    for eventname in sort_columns:
        if eventname in Append_info_end.keys():
            pass
        else:
            outputstring += eventname + '--->'# '--> \n'
    

    #final stellar types and hubble time dont have a chronological counter so
    #if we filter on these, just append that info at the end.

   

    final_info = ''
    for info in list(Append_info_end.keys()):
        if info in Columns:
            text1=Append_info_end[info][0]
            star = line[info]
            stellar_type = linker(Append_info_end[info][1], star)
            #print info,'!!', star, '??', stellar_type
            text = text1 + stellar_type
            final_info += text
    outputstring += final_info
    return outputstring

