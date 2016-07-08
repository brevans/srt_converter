# srt_converter

For the bird man Sam Snow.

run this python script in a directory with exported .srt caption files to get more usable data.

```bash
python srt_2_csv.py
```
You need:
 * python 3+
 * the file in this repo, ```stake_coords.csv```
 * .srt files

## SRT File specs
 The srt filename needs to have a date (format YYYYMMDD) in the first field if split by underscores. The date can have extra letters before or after. Each 4-line entry in an srt file looks like:

```
2
00:03:53,367 --> 00:06:30,434
The quick brown fox

```
Line 1 is the caption numer, starting with 1.  
Line 2 is the start and stop of the caption, relative to the beginning of the video in Hours:Minutes:Seconds,Milliseconds  
The third line is the string of text for the caption.  
The fourth line is always empty, and assumed to be so.

#### Snow Format

The behavior data is encoded as semicolon separated fields (trailing and leading whitespace is removed) in the text of the captions. The captions that this script pays attention to fall into four categories, others are ignored. Examples and descriptions below.

_**Atomic_Clock:**_  
```
1
00:00:03,667 --> 00:03:53,367
Atomic_clock; 6:46:11;

```
Text fields (must be exactly two):  
1. The text "Atomic_clock"  
2. The local time, measured in Hours:Minutes:Seconds  

_**Position:**_
```
20
00:15:00,067 --> 00:15:02,500
Position; 705; H5; 2.5; 6.5; 351; H6; 6.5; 1; 315; H5; 7; 9; 710; H6; 9; 0; 340; H5; 9.5; 9.5; 702; I6; 0; 0

```
Text fields (First field, then mutiples of 4):  
1. The text "Position"  
2. Bird ID  
3. Grid stake ID  
4. X Offset relative to stake  
5. Y Offset relative to stake  
Repeat 2-5  

_**Interactions:**_  
There are two types of interaction captions that get parsed.  
_**start:**_
```
12
00:12:01,567 --> 00:12:03,834
710; 3; start; 702; H6; 7.5; 1; I6; 0; 0;Y; SI; #strutting interrupted from a distance

```
Text fields (First field, then mutiples of 4):  
1. Initiator ID  
2. Interaction Number  
3. The text "start"  
4. Partner ID  
5. Initiator stake  
6. Initiator X offset relative to initiator stake  
7. Initiator Y offset relative to initiator stake  
8. Partner stake  
9. Partner X offset relative to partner stake  
10. Partner Y offset relative to partner stake  
11. Females Present  
12. Reaction Code  
13. Other notes  

_**end:**_
```
11
00:11:29,300 --> 00:12:01,567
710; 2; end; 702; 710; 2; FO; #unclear who disengages

```
Text fields (exactly 8):  
1. Initiator ID  
2. Interaction Number  
3. The text "end"  
4. Partner ID  
5. Disengager ID  
6. Bouts Of Smacking: a number  
7. Face off: either either FO, CH or NA  
8. Other notes  


## Output
The output files are:  
 * < input filename >_interactions.csv
 * < input filename >_positions.csv

#### Interactions output file columns:
1. **Lek_Date_ID**: the first portion of the file name, if split by underscores. e.g. "CHG20140326"
2. **Time_Stamp**: Date and time, based on atomic clock in video, with no timezone, in [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format
3. **Initiator_ID**: should match between start and end entry
4. **Interaction_Number**: should match between start and end entry
5. **Partner_ID**: should match between start and end entry
6. **Females_Present**: from start entry
7. **Reaction_Code**: from start entry
8. **Disengager_ID**: from end entry
9. **Bouts_O_Smacking**: from end entry
10. **Duration**: end - start times
11. **Initiator_Cartesian_X**: corrected initiator X coordinate, based on stake_coords.csv
12. **Initiator_Cartesian_Y**: corrected initiator Y coordinate, based on stake_coords.csv
13. **Partner_Cartesian_X**: corrected partner Y coordinate, based on stake_coords.csv
14. **Partner_Cartesian_Y**: corrected partner Y coordinate, based on stake_coords.csv
15. **Other_notes**: notes from both start and end

#### Positions output columns:
1. **Lek_Date_ID**: the first portion of the file name, if split by underscores. e.g. "CHG20140326"
2. **Time_Stamp**: Date and time, based on atomic clock in video, with no timezone, in [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format
3. **Bird_ID**: Bird Identifier from position entry
4. **X_Offset**: X offset from position entry
5. **Y_Offset**: Y offset from position entry
6. **Cartesian_X**: corrected X coordinate, based on stake_coords.csv
7. **Cartesian_Y**: corrected y coordinate, based on stake_coords.csv
