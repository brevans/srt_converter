#!/usr/bin/env python
from datetime import datetime
from glob import glob

#set up columns
all_columns = ['Time_of_Day', 'Time_Stamp', 'Initiator_ID', 'Interaction_Number', 'Data_Type', 'Partner_ID', 
               'Initiator_Stake', 'Initiator_X', 'Initiator_Y',
               'Partner_Stake', 'Partner_X', 'Partner_Y', 'Females_Present', 
               'Reaction_Code', 'Disengager_ID', 'Bouts_O_Smacking', 'Other_notes']

start_columns = ['caption_number', 'Time_Stamp', 'Initiator_ID', 'Interaction_Number', 'Data_Type', 'Partner_ID', 
                 'Initiator_Stake', 'Initiator_X', 'Initiator_Y',
                 'Partner_Stake', 'Partner_X', 'Partner_Y', 'Females_Present', 
                 'Reaction_Code', 'Other_notes']
                 

end_columns = ['caption_number', 'Time_Stamp', 'Initiator_ID', 'Interaction_Number', 'Data_Type', 'Partner_ID', 
               'Disengager_ID', 'Bouts_O_Smacking', 'Other_notes']

def parse_srt(fn):
    data_in = []
    fh = open(fn)

    while True:
        try:
            caption_number = next(fh).rstrip("\n")
            time_stamp = next(fh).split(' --> ')[0].replace(',','.')
            data = [x.rstrip().lstrip() for x in next(fh).split(';')]
            toss_me = next(fh)
            data_in.append([caption_number, time_stamp]+data)
        except StopIteration:
            break

    data_out=[]
    for d in data_in:
        if d[2] == 'Atomic_clock':
            atomic_time = datetime.strptime(d[3], "%H:%M:%S")-datetime.strptime(d[1], "%H:%M:%S.%f")
        elif d[2] == 'Position':
            pass #do something about position data
        elif len(d) >= len(end_columns):
            if d[4] == 'start':
                assert len(start_columns) == len(d), "Number of columns doesn't match for a start at caption number {}.".format(d[0])
                data_out.append(dict(zip(start_columns, d)))
            elif d[4] == 'end':
                assert len(end_columns) == len(d), "Number of columns doesn't match for an end at caption number {}.".format(d[0])
                data_out.append(dict(zip(end_columns, d)))

    for d in data_out:
        d['Time_of_Day']=str(atomic_time+datetime.strptime(d['Time_Stamp'], "%H:%M:%S.%f")).split(' ')[1]
    return data_out

def data_2_csv(fn, data_out):
    csv_out = open(fn.replace('.srt','.csv'), 'w')
    csv_out.write(','.join(all_columns)+'\n')
    for datum in data_out:
        csv_out.write(','.join([datum[x] if x in datum else 'NA' for x in all_columns])+'\n')
    csv_out.close()

if __name__ == "__main__":
    for srt in glob('*.srt'):
        dout = parse_srt(srt)
        data_2_csv(srt, dout)
        