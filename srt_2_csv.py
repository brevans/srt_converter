#!/usr/bin/env python
from datetime import datetime
from operator import itemgetter
from glob import glob
import os
import re

#set up columns
interaction_columns = ['Lek_Date_ID', 'Time_Stamp', 'Initiator_ID', 
               'Interaction_Number', 'Partner_ID', 'Females_Present',
               'Reaction_Code', 'Disengager_ID', 'Bouts_O_Smacking', 'Face_Off',
               'Duration', 'Initiator_Cartesian_X', 'Initiator_Cartesian_Y',
               'Partner_Cartesian_X', 'Partner_Cartesian_Y', 'Other_Notes']

start_columns = ['caption_number', 'Caption_Stamp', 'Initiator_ID', 
                 'Interaction_Number', 'Data_Type', 'Partner_ID', 
                 'Initiator_Stake', 'Initiator_X', 'Initiator_Y',
                 'Partner_Stake', 'Partner_X', 'Partner_Y', 
                 'Females_Present', 'Reaction_Code', 'Other_Notes']
                 

end_columns = ['caption_number', 'Caption_Stamp', 'Initiator_ID', 
               'Interaction_Number', 'Data_Type', 'Partner_ID', 
               'Disengager_ID', 'Bouts_O_Smacking', 'Face_Off', 'Other_Notes']
               
ind_pos_columns = ['Bird_ID', 'Grid_Stake', 'X_Offset', 'Y_Offset']

pos_columns = ['Lek_Date_ID','Time_Stamp','Caption_Stamp', 'Bird_ID', 'Grid_Stake',
               'X_Offset', 'Y_Offset', 'Cartesian_X', 'Cartesian_Y']

def make_stake_dict(fn):
    fh = open(fn)
    d = {}
    header = next(fh)
    for l in fh:
        tmp = l.split(',')
        d[tmp[0]] = [int(x) for x in tmp[1:]]
    return d

def parse_srt(fn, stake_fn):
    data_in = []
    stake_offset = make_stake_dict(stake_fn)
    fh = open(fn)
    lek_date_id = os.path.basename(fn).split('_')[0]
    while True:
        try:
            caption_number = next(fh).rstrip("\n")
            #keep start of caption interval, floor to whole seconds
            caption_stamp = next(fh).split(' --> ')[0].split(',')[0]
            data = [x.lstrip().rstrip() for x in next(fh).rstrip().rstrip(';').lstrip().split(';')]
            toss_me = next(fh)
            #every data line is caption number, time_stamp + its fields
            data_in.append([caption_number, caption_stamp]+data)
        except StopIteration:
            break

    interactions = []
    start_ints = []
    end_ints = []
    positions = []
    atomic_time = None
    for d in data_in:
        if d[2] == 'Atomic_clock': #get atomic time, offset
            atomic_time = (datetime.strptime(d[3], "%H:%M:%S") -
                           datetime.strptime(d[1], "%H:%M:%S"))
        if d[2].lower()=='position': #parse out individual positions
            assert (len(d)-3)%len(ind_pos_columns)==0, " Wrong number of bird position fields at caption number {} in file {}".format(d[0], fn)
            try:
                for (bid, stn, xoff, yoff) in zip(d[3::4],d[4::4],d[5::4],d[6::4]):
                    ind_pos = dict(zip(ind_pos_columns, [bid, stn, xoff, yoff]))
                    ind_pos['Lek_Date_ID'] = lek_date_id
                    ind_pos['Caption_Stamp'] = d[1]
                    #convert postions to cartesian
                    ind_pos['Cartesian_X'] = str(stake_offset[ind_pos['Grid_Stake']][0]+ float(ind_pos['X_Offset']))
                    ind_pos['Cartesian_Y'] = str(stake_offset[ind_pos['Grid_Stake']][1]+ float(ind_pos['Y_Offset']))
                    positions.append(ind_pos)
            except Exception as e:
                print("something looks wrong with your position data at caption {}: {} \n   in file {}".format(d[0], e, fn))

        if len(d) >= len(end_columns) and (d[4].lower()=='start' or d[4].lower()=='end'):
            try:
                if d[4].lower() == 'start':
                    assert len(start_columns) == len(d), "Number of columns doesn't match."
                    start_ints.append(dict(zip(start_columns, d)))
                if d[4].lower() == 'end':
                    assert len(end_columns) == len(d), "Number of columns doesn't match."
                    end_ints.append(dict(zip(end_columns, d)))
            except Exception as e:
                print("something looks wrong with your start or stop at caption {}: {} \n    in file {}".format(d[0], e, fn))
    
    assert atomic_time is not None, "Didn't find an atomic time entry in file {}, can't calulate proper Time_Stamp!".format(fn)
    
    #convert caption times to date time stamps
    for i in [start_ints, end_ints]:
        for j in i:
            caption_string = re.sub(r"\D", "", lek_date_id) + j['Caption_Stamp']
            j['Time_Stamp'] = atomic_time+datetime.strptime(caption_string, "%Y%m%d%H:%M:%S")
    for p in positions:
        caption_string = re.sub(r"\D", "", lek_date_id) + p['Caption_Stamp']
        p['Time_Stamp'] = (atomic_time+datetime.strptime(caption_string, "%Y%m%d%H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S")
        
    # stitch together start and end entries, sort each then compare and complain 
    for start_int, end_int in zip(sorted(start_ints, key=itemgetter('Initiator_ID', 'Interaction_Number')), 
                                  sorted(end_ints, key=itemgetter('Initiator_ID', 'Interaction_Number'))):
        assert len(start_ints) == len(end_ints), "error, different number of start ({}) and end ({}) entries in file: {}".format(len(start_int), len(end_int), fn)
        assert start_int['Initiator_ID'] == end_int['Initiator_ID'], "Initiator ID mismatch in start&stop captions {}, {}, file {}".format(start_int['caption_number'], end_int['caption_number'])
        assert start_int['Partner_ID'] == end_int['Partner_ID'], "Partner ID mismatch in start&stop captions {}, {}, file {}".format(start_int['caption_number'], end_int['caption_number'])
        assert start_int['Interaction_Number'] == end_int['Interaction_Number'], "Interaction Number mismatch in start&stop captions {}, {}, file {}".format(start_int['caption_number'], end_int['caption_number'])
        interact = {}
        interact['Lek_Date_ID'] = lek_date_id
        interact['Time_Stamp'] = start_int['Time_Stamp'].strftime("%Y-%m-%d %H:%M:%S")
        interact['Initiator_ID'] = start_int['Initiator_ID']
        interact['Interaction_Number'] = start_int['Interaction_Number']
        interact['Partner_ID'] = start_int['Interaction_Number']
        interact['Females_Present'] = start_int['Females_Present']
        interact['Reaction_Code'] = start_int['Reaction_Code']
        interact['Disengager_ID'] = end_int['Disengager_ID']
        interact['Bouts_O_Smacking'] = end_int['Bouts_O_Smacking']
        interact['Face_Off'] = end_int['Face_Off']
        interact['Duration'] = str((end_int['Time_Stamp'] - start_int['Time_Stamp']).seconds)
        interact['Initiator_Cartesian_X'] = str(stake_offset[start_int['Initiator_Stake']][0]+ float(start_int['Initiator_X']))
        interact['Initiator_Cartesian_Y'] = str(stake_offset[start_int['Initiator_Stake']][1]+ float(start_int['Initiator_Y']))
        interact['Partner_Cartesian_X'] = str(stake_offset[start_int['Partner_Stake']][0]+ float(start_int['Partner_X']))
        interact['Partner_Cartesian_Y'] = str(stake_offset[start_int['Partner_Stake']][1]+ float(start_int['Partner_Y']))
        interact['Other_Notes'] = start_int['Other_Notes'] + ' ' + end_int['Other_Notes']
        interactions.append(interact)
        
    return sorted(interactions, key=itemgetter('Time_Stamp')), positions

def data_2_csv(fn, interactions, positions):
    csv_inte = open(fn.replace('.srt','_interactions.csv'), 'w')
    csv_inte.write(','.join(interaction_columns)+'\n')
    for inter in interactions:
        csv_inte.write(','.join([inter[x] for x in interaction_columns])+'\n')
    csv_inte.close()
    
    csv_posi = open(fn.replace('.srt','_positions.csv'), 'w')
    csv_posi.write(','.join(pos_columns)+'\n')
    for posi in positions:
        csv_posi.write(','.join([posi[x] for x in pos_columns])+'\n')
    csv_posi.close()
    

if __name__ == "__main__":
    stakes = 'stake_coords.csv'
    for srt in glob('*.srt'):
        print('Working on file {} ...'.format(srt))
        interactions, positions = parse_srt(srt, stakes)
        data_2_csv(srt, interactions, positions)
        print('Done.')