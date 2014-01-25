#!/usr/bin/env python
# -*- coding: utf8 -*-

# Examples:
# KT1D-1,K,NA,3504.6,80m,NR4M,K,NA,CQ,35,2009-02-21 00:00:02+00,,,20090221,1235199602
# WA7LNW,K,NA,28239,10m,AL7FS,KL,NA,DX,3,2013-12-12 23:59:59,12,CW,20131212,1386917999

# POSTER, POSTER-COUNTRY-PREFIX, POSTER-CONTINENT, FREQUENCY (kHz), BAND, DX, DX-COUNTRY-PREFIX, DX-CONTINENT, CQ, SNR (dB), DATE-AND-TIME, WPM, MODE, DATE, UNIX-EPOCH

# 0: POSTER
# 1: POSTER-COUNTRY-PREFIX
# 2: POSTER-CONTINENT
# 3: FREQUENCY (kHz)
# 4: BAND
# 5: DX
# 6: DX-COUNTRY-PREFIX
# 7: DX-CONTINENT
# 8: CQ
# 9: SNR (dB)
# 10: DATE-AND-TIME
# 11: WPM
# 12: MODE
# 13: DATE
# 14: UNIX-EPOCH
 
import datetime
import math
import os
import sys
import time
 
# rank-sig CALL BAND CONTINENT START-DATE END-DATE

MAX_TIME_DIFFERENCE = 600  # maximum difference in seconds for comparisons

data_filename='/zfs1/data/rbn/rbndata.csv'    # location of the RBN data
 
target_call = sys.argv[1]

band = '20m'     # default
continent = 'EU' # default

# dates may be either integers or strings
start_date = 00000000  # default
end_date   = 30000000  # default

if len(sys.argv) > 2:
  band = sys.argv[2]

if len(sys.argv) > 3:
  continent = sys.argv[3]

if len(sys.argv) > 4:
  start_date = int(sys.argv[4])

if len(sys.argv) > 5:
  end_date = int(sys.argv[5])
  
# create an array of short lines
call_lines = []

# short_line:
# 0: POSTER
# 1: POSTER-CONTINENT
# 2: BAND
# 3: DX
# 4: SNR (dB)
# 5: DATE
# 6: UNIX-EPOCH

for line in sys.stdin:
  fields = line.split(',')  
  my_continent = fields[7]
  short_line = [ fields[0], fields[2], fields[4], fields[5], int(fields[9]), int(fields[13]), int(fields[14]) ] 
  call_lines.append(short_line)
  
#print "call lines: ", len(call_lines) 
 
# extract the lines with the target continent
poster_continent_lines = []

for short_line in call_lines:
  this_continent = short_line[1]
  
  if this_continent == continent:
    poster_continent_lines.append(short_line)

#print "poster continent lines: ", len(poster_continent_lines) 
    
# extract the lines within the target date range
# (could eliminate this in the case that the dates are the default values,
# and copy continent_lines directly to date_lines))
date_lines = []

for short_line in poster_continent_lines:
  this_date = short_line[5]

  if this_date >= start_date and this_date <= end_date:
    date_lines.append(short_line)

# extract the lines on the target band
band_lines = []

for short_line in date_lines:
  this_band = short_line[2]
  if this_band == band:
    band_lines.append(short_line)
    
if len(band_lines) == 0:
  exit
    
my_lines = band_lines    # just to make it more obvious; my_lines contains all the short lines for baseline QSOs

# slow, simple, but does the job
results = {}  # key is epoch, value is a list of SNR measurements, of which the first is *my* signal at the poster

with open(data_filename, 'r') as fp:    # handles opening and closing; read the entire RBN dataset
  
  for line in fp:
    fields = line.split(',')
    
    if fields[7] != my_continent:   # we are interested only in stations posted on the same continent
      continue
    
    if fields[4] != band:           # and on the same band
      continue
    
    if fields[2] != continent:      # and on the target continent
      continue
    
    if fields[5] == target_call:    # don't compare postings of me
      continue
    
    rbn_time = int(fields[14])      # epoch seconds
    remove_lines = []               # lines we can remove from my_lines because we've passed the relevant epoch
    
    for my_line in my_lines:
      
      if not results.has_key(my_line[6]):
	results[my_line[6]] = [ my_line[4] ]    # key is epoch, value is my SNR
      
      minimum_time = my_line[6] - MAX_TIME_DIFFERENCE
      maximum_time = my_line[6] + MAX_TIME_DIFFERENCE
      
      if rbn_time > maximum_time:        # the datasets MUST be in chronological order
        remove_lines.append(my_line)     # we will remove this line shortly
        
      if rbn_time >= minimum_time and rbn_time <= maximum_time:  # there is a match in time
        my_poster = my_line[0]
        rbn_poster = fields[0]
        
        if rbn_poster != my_poster:      # we require that the same station made both posts
	  continue
	
        results[my_line[6]].append(int(fields[9]))    # append the SNR of another station
 
    for line_to_remove in remove_lines:    # now we can remove lines whose (epoch + MAX_TIME_DIFFERENCE) we have passed
      my_lines.remove(line_to_remove)

# NB: dictionaries are unsorted; print to standard output
for epoch, values in results.iteritems():
  print epoch,
  for value in values:
    print value,
  print


  


