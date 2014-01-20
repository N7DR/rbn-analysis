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
 
# restrict results to only comparisons that lie in the range ±20 
 
target_call = [sys.argv[1:2], sys.argv[2:3]]

band = '20m'     # default
continent = 'EU' # default

start_date = 00000000
end_date   = 30000000

time_diff = 600

if len(sys.argv) >= 3:
  band = sys.argv[3]

if len(sys.argv) >= 4:
  continent = sys.argv[4]

if len(sys.argv) >= 5:
  start_date = int(sys.argv[5])

if len(sys.argv) >= 6:
  end_date = int(sys.argv[6]) 
  
call_lines = [[] for x in range(2)]

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
  this_call = fields[5:6]
  for n in range(2):
    if this_call == target_call[n]:
      short_line = [ fields[0], fields[2], fields[4], fields[5], int(fields[9]), int(fields[13]), int(fields[14]) ] 
      call_lines[n].append(short_line)

continent_lines = [[] for x in range(2)]

for n in range(2):
  for short_line in call_lines[n]:
    this_continent = short_line[1]
    if this_continent == continent:
      continent_lines[n].append(short_line)

date_lines = [[] for x in range(2)]

for n in range(2):
  for short_line in continent_lines[n]:
    this_date = short_line[5]
    if this_date >= start_date and this_date <= end_date:
      date_lines[n].append(short_line)
      
sigs = []

for short_line_1 in date_lines[0]:
  seconds_1 = short_line_1[6]
  spotter_1 = short_line_1[0]
  band_1 = short_line_1[2]
  
  for short_line_2 in date_lines[1]:
    seconds_2 = short_line_2[6]
    spotter_2 = short_line_2[0]
    band_2 = short_line_2[2]
  
    if spotter_1 == spotter_2 and abs(seconds_1 - seconds_2) <= time_diff and band_1 == band and band_2 == band:
      snr_1 = short_line_1[4]
      snr_2 = short_line_2[4]
      difference = snr_2 - snr_1
      if abs(difference) <= 20:
	sigs.append(difference)
    
    if seconds_2 > seconds_1 + time_diff:  # no need to check any more
      break

for snr in sigs:
  print snr
  


