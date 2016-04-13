#!/usr/bin/env python
from datetime import datetime
import os
from glob import glob

#set up columns
interaction_columns = ['Time_of_Day', 'Time_Stamp', 'Initiator_ID', 
               'Interaction_Number', 'Data_Type', 'Partner_ID', 
               'Initiator_Stake', 'Initiator_X', 'Initiator_Y',
               'Partner_Stake', 'Partner_X', 'Partner_Y', 'Females_Present', 
               'Reaction_Code', 'Disengager_ID', 'Bouts_O_Smacking',
               'Other_notes']

start_columns = ['caption_number', 'Time_Stamp', 'Initiator_ID', 
                 'Interaction_Number', 'Data_Type', 'Partner_ID', 
                 'Initiator_Stake', 'Initiator_X', 'Initiator_Y',
                 'Partner_Stake', 'Partner_X', 'Partner_Y', 
                 'Females_Present', 'Reaction_Code', 'Other_notes']
                 

end_columns = ['caption_number', 'Time_Stamp', 'Initiator_ID', 
               'Interaction_Number', 'Data_Type', 'Partner_ID', 
               'Disengager_ID', 'Bouts_O_Smacking', 'Other_notes']
               
ind_pos_columns = ['Bird_ID', 'Grid_Steak', 'X_offset', 'Y_Offset']

pos_columns = ['Lek_Date','Time_of_Day','Time_Stamp', 'Bird_ID', 'Grid_Steak', 'X_offset', 'Y_Offset']

def parse_srt(fn):
    data_in = []
    fh = open(fn)
    lek_date_id = os.path.basename(fn).split('_')[0]
    while True:
        try:
            caption_number = next(fh).rstrip("\n")
            time_stamp = next(fh).split(' --> ')[0].replace(',','.')
            data = [x.lstrip().rstrip() for x in next(fh).rstrip().rstrip(';').lstrip().split(';')]
            toss_me = next(fh)
            #every data line is caption number, time_stamp + its fields
            data_in.append([caption_number, time_stamp]+data)
        except StopIteration:
            break

    interactions = []
    positions = []
    atomic_time = None
    for d in data_in:
        if d[2] == 'Atomic_clock': #get atomic time, offset
            atomic_time = (datetime.strptime(d[3], "%H:%M:%S")-
                           datetime.strptime(d[1], "%H:%M:%S.%f"))
        if ('Position' in d) or ('position' in d): #parse out individual positions
            assert (len(d)-3)%len(ind_pos_columns)==0, " Wrong number of bird position fields at caption number {}".format(d[0])
            try:
                for (bid, stn, xoff, yoff) in zip(d[3::4],d[4::4],d[5::4],d[6::4]):
                    ind_pos = dict(zip(ind_pos_columns, [bid, stn, xoff, yoff]))
                    ind_pos['Lek_Date'] = lek_date_id
                    ind_pos['Time_Stamp'] = d[1]
                    positions.append(ind_pos)
            except Exception as e:
                print("something looks wrong with your position data at caption {}: {}".format(d[0], e))

        if ('start' in d) or ('stop' in d):
            try:
                if d[4] == 'start':
                    assert len(start_columns) == len(d), "Number of columns doesn't match for a start at caption number {}.".format(d[0])
                    interactions.append(dict(zip(start_columns, d)))
                elif d[4] == 'end':
                    assert len(end_columns) == len(d), "Number of columns doesn't match for an end at caption number {}.".format(d[0])
                    interactions.append(dict(zip(end_columns, d)))
            except Exception as e:
                print("something looks wrong with your start or stop at caption {}: {}".format(d[0], e))
    
    assert atomic_time is not None, "Didn't find an atomic time entry, can't calulate proper Time_of_Day!"
    
    for i in interactions:
        i['Time_of_Day']=str(atomic_time+datetime.strptime(i['Time_Stamp'], "%H:%M:%S.%f")).split(' ')[1].split('.')[0]
    for p in positions:
        p['Time_of_Day']=str(atomic_time+datetime.strptime(p['Time_Stamp'], "%H:%M:%S.%f")).split(' ')[1].split('.')[0]

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
    for srt in glob('*.srt'):
        interactions, positions = parse_srt(srt)
        data_2_csv(srt, interactions, positions)
        