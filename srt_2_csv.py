#!/usr/bin/env python
from datetime import datetime
import os
import re
from glob import glob

#set up columns
interaction_columns = ['Lek_Date_ID', 'Time_Stamp', 'Caption_Stamp', 'Initiator_ID', 
               'Interaction_Number', 'Data_Type', 'Partner_ID', 
               'Initiator_Stake', 'Initiator_X', 'Initiator_Y',
               'Partner_Stake', 'Partner_X', 'Partner_Y', 'Females_Present', 
               'Reaction_Code', 'Disengager_ID', 'Bouts_O_Smacking',
               'Other_notes']

start_columns = ['caption_number', 'Caption_Stamp', 'Initiator_ID', 
                 'Interaction_Number', 'Data_Type', 'Partner_ID', 
                 'Initiator_Stake', 'Initiator_X', 'Initiator_Y',
                 'Partner_Stake', 'Partner_X', 'Partner_Y', 
                 'Females_Present', 'Reaction_Code', 'Other_notes']
                 

end_columns = ['caption_number', 'Caption_Stamp', 'Initiator_ID', 
               'Interaction_Number', 'Data_Type', 'Partner_ID', 
               'Disengager_ID', 'Bouts_O_Smacking', 'Other_notes']
               
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
                    ind_pos['Cartesian_X'] = str(stake_offset[ind_pos['Grid_Stake']][0]+ float(ind_pos['X_Offset']))
                    ind_pos['Cartesian_Y'] = str(stake_offset[ind_pos['Grid_Stake']][1]+ float(ind_pos['Y_Offset']))
                    positions.append(ind_pos)
            except Exception as e:
                print("something looks wrong with your position data at caption {}: {} \nin file {}".format(d[0], e, fn))

        if len(d) >= 8 and (d[4].lower()=='start' or d[4].lower()=='end'):
            try:
                if d[4].lower() == 'start':
                    assert len(start_columns) == len(d), "Number of columns doesn't match."
                    interactions.append(dict(zip(start_columns, d)))
                if d[4].lower() == 'end':
                    assert len(end_columns) == len(d), "Number of columns doesn't match."
                    interactions.append(dict(zip(end_columns, d)))
            except Exception as e:
                print("something looks wrong with your start or stop at caption {}: {} \n    in file {}".format(d[0], e, fn))
    
    assert atomic_time is not None, "Didn't find an atomic time entry in file {}, can't calulate proper Time_Stamp!".format(fn)
    
    for i in interactions:
        caption_string = re.sub(r"\D", "", lek_date_id) + i['Caption_Stamp']
        i['Time_Stamp'] = (atomic_time+datetime.strptime(caption_string, "%Y%m%d%H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S")
    for p in positions:
        caption_string = re.sub(r"\D", "", lek_date_id) + p['Caption_Stamp']
        p['Time_Stamp'] = (atomic_time+datetime.strptime(caption_string, "%Y%m%d%H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S")

    return interactions, positions

def data_2_csv(fn, interactions, positions):
    csv_inte = open(fn.replace('.srt','_interactions.csv'), 'w')
    csv_inte.write(','.join(interaction_columns)+'\n')
    for inter in interactions:
        csv_inte.write(','.join([inter[x] if x in inter else 'NA' for x in interaction_columns])+'\n')
    csv_inte.close()
    
    csv_posi = open(fn.replace('.srt','_positions.csv'), 'w')
    csv_posi.write(','.join(pos_columns)+'\n')
    for posi in positions:
        csv_posi.write(','.join([posi[x] for x in pos_columns])+'\n')
    csv_posi.close()
    

if __name__ == "__main__":
    stakes = 'stake_coords.csv'
    for srt in glob('*.srt'):
        interactions, positions = parse_srt(srt, stakes)
        data_2_csv(srt, interactions, positions)
        