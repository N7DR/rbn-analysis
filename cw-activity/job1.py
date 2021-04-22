#!/usr/bin/env python3

import calendar
import datetime
import math
import pandas as pd
import subprocess
import sys

filename = '/zd1/rbn/rbndata.csv'

# -----------------------  nothing below this line should need ot be changed  -------------------------------

min_year = int(sys.argv[1])
max_year = int(sys.argv[2])
OUT_DIR = sys.argv[3]
UPPER_BOUND = sys.argv[4]
n_values = int(sys.argv[5])

start_seconds = []	    # starts of years
start_seconds_10 = []       # starts of deciyears

# function to take an epoch and return an index into start_seconds_10
def index(epoch) :
  if epoch < start_seconds_10[0] :    # too early
    return 9999
  
  ix = -1
  
  for marker in start_seconds_10 :
    ix = ix + 1
    
    if epoch < start_seconds_10[ix] :
      return (ix - 1)
  
  return 9999

# for each deciyear, get the number of calls that appear 1, 2, 3, ... UPPER_BOUND times
def values_1_N(UB) :
  n_deciyears = ((max_year - min_year) + 1) * n_values    # number of deciyears

  for band in hf_bands_plus :
    band_name = str(band)
  
    if band == 0 :
      band_name = 'HF'
  
    filename = OUT_DIR + '/exact_appearances_1_' + str(UB) + '.' + band_name
    fh = open(filename, 'w')
  
    for bound in range(1, int(UB) + 1) :
      n_calls = [0] * n_deciyears
    
      for ix in range(0, n_deciyears) :
        call_dict = (call_list[band])[ix]
          
        for call in call_dict :
          n_this_call = call_dict[call]
             
          if n_this_call == bound :
            n_calls[ix] = n_calls[ix] + 1
      
        separator = ''
        if ix != (n_deciyears - 1) :
          separator = ','
        
        fh.write(str(n_calls[ix]) + separator)
      fh.write('\n')
    fh.close()

# this is taken from convert-rbn; starts of years in seconds
for year in range(min_year, max_year + 2) :		# need to find start of year after max_year
  d = datetime.datetime(year, 1, 1, 0, 0, 0, 0, None)
  seconds = calendar.timegm(d.utctimetuple())           # actual UTC epoch
  start_seconds.append(seconds)

# calculate starts of deciyears
for year in range(min_year, max_year + 1) :
  relative_year = year - min_year
  start_this_year = start_seconds[relative_year]
  start_next_year = start_seconds[relative_year + 1]
  seconds_in_this_year = start_next_year - start_this_year
  for deciyear in range(0, n_values) :			# 0 .. 9
    seconds = start_this_year + ((start_next_year - start_this_year) * deciyear) / n_values
    start_seconds_10.append(int(seconds + 0.5))
    
# append the start of the year after max_year
start_seconds_10.append(start_seconds[max_year + 1 - min_year])

# call list is a map; key = band; value = map<callsign, number_of_times_it_appears>

call_list = {}

hf_bands = [ 160, 80, 40, 30, 20, 17, 15, 12, 10 ]
hf_bands_plus = [ 160, 80, 40, 30, 20, 17, 15, 12, 10, 0 ]            # 0 is for HF
hf_bands_m = [ '160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m' ]

# create copies for each band
for band in hf_bands_plus :
  call_list[band] = []
  
  for n in range(0, len(start_seconds_10)) :
    call_list[band].append({})				# insert empty dictionary; { callsign : n_appearances }

# K1FC,K,NA,7021,40m,XE2T,XE,NA,CQ,7,2020-01-01 00:00:01,20,CW,20200101,1577836801

fh = open(filename)

while True:
  line = fh.readline()
  
  if len(line) == 0 :
    break
  
  line = line.strip()

  fields = line.split(",")
  epoch = int(fields[14])
  
  if epoch >= start_seconds_10[len(start_seconds_10) - 1] : # are we past the last value in start_seconds_10?
    break
	
  if epoch >= start_seconds_10[0] :   # if not too early
    ix = index(epoch)
  
    if ix == 9999 :	# should never be true
      print(epoch)
      exit()
  
    callsign = fields[5]

    is_cw = (fields[12] == '') or (fields[12] == 'CW')

    if fields[4] in hf_bands_m :
      if is_cw : 
        band = int(fields[4][:-1])
        
        if callsign in (call_list[band])[ix] :
          (call_list[band])[ix][callsign] = (call_list[band])[ix][callsign] + 1
        else :
          (call_list[band])[ix][callsign] = 1
  
        if callsign in (call_list[0])[ix] :       # HF
          (call_list[0])[ix][callsign] = (call_list[0])[ix][callsign] + 1
        else :
          (call_list[0])[ix][callsign] = 1
 
fh.close()
    
# for each deciyear, get and write the number of calls that appear 1, 2, 3, ... UPPER_BOUND times
values_1_N(UPPER_BOUND)

# for each deciyear from MIN_YEAR to MAX_YEAR+0.9, estimate the first "large" value of n. using the HF files
filename = OUT_DIR + '/exact_appearances_1_' + str(UPPER_BOUND) + '.HF'

df = pd.read_csv(filename, header=None)

upper_bound = 0

nv = (max_year - min_year) * n_values

for ix in range(0, nv) :
  vn = df[ix]    # the V(n) values for the deciyear

  for nm1 in range(0, len(vn) - 2) :
    v1 = vn[nm1]
    if v1 != 0 :
      min_val = v1 - 2 * math.sqrt(v1)
      max_val = v1 + 2 * math.sqrt(v1)
    
      v2 = vn[nm1 + 1]
      if (v2 != 0) and (v2 >= min_val) and (v2 <= max_val) : 
        min_val2 = v2 - 2 * math.sqrt(v2)
        max_val2 = v2 + 2 * math.sqrt(v2)
        
        v3 = vn[nm1 + 2]
        if (v3 != 0) and (v3 >= min_val2) and (v3 <= max_val2) :
          if (nm1 + 1) > upper_bound :
            upper_bound = nm1 + 1
          break

upper_bound = (int(upper_bound / 5) * 5) + 5

print(upper_bound)

# for each deciyear, get and write the number of calls that appear 1, 2, 3, ... upper_bound times
values_1_N(upper_bound)
  
# for each year from MIN_YEAR to MAX_YEAR, get the number of calls that
# appear LOWER_BOUND or more times times

# extract the appearance data for >= LOWER_BOUND appearances for each year for a specific band, and write to a file
  
#$OUT_DIR/ge$LOWER_BOUND.$1  
lower_bound = upper_bound + 1

n_deciyears = ((max_year - min_year) + 1) * n_values    # number of deciyears

for band in hf_bands_plus :
  
  band_name = str(band)
  
  if band == 0 :
    band_name = 'HF'
  
  filename = OUT_DIR + '/' + 'ge' + str(lower_bound) + '.' + band_name
  fh = open(filename, 'w')
  
  n_calls = [0] * n_deciyears
    
  for ix in range(0, n_deciyears) :
    call_dict = (call_list[band])[ix]
          
    for call in call_dict :
      n_this_call = call_dict[call]
             
      if n_this_call >= lower_bound :
        n_calls[ix] = n_calls[ix] + 1
      
    separator = ''
    if ix != (n_deciyears - 1) :
      separator = ','
        
    fh.write(str(n_calls[ix]) + separator)
      
  fh.write('\n')

fh.close()
