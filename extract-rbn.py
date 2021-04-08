#!/usr/bin/env python2
# -*- coding: utf8 -*-

# extract RBN data for a range of dates

# rbn-extract YYYYMMDD YYYYMMDD

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
 
import calendar
import datetime
import os
import subprocess
import sys

#data_filename='/zfs1/data/rbn/rbndata.csv'    # location of the RBN data
data_filename='/zd1/rbn/rbndata.csv'    # location of the RBN data

# is rbncat available? For most users this should NOT be "true"
#export RBNCAT="false"
RBNCAT = True

# -- Nothing below this line should need to be changed  

pid = os.getpid()

# dates may be either integers or strings
start_date_str = '00000000'  # default
end_date_str   = '30000000'  # default

if len(sys.argv) > 1:
  start_date_str = sys.argv[1]

if len(sys.argv) > 2:
  end_date_str = sys.argv[2]
 
year_start = start_date_str[:4]
month_start = start_date_str[4:6]
day_start = start_date_str[6:8]

start = datetime.date(int(year_start), int(month_start), int(day_start))

year_end = end_date_str[:4]
month_end = end_date_str[4:6]
day_end = end_date_str[6:8]

end = datetime.date(int(year_end), int(month_end), int(day_end))

search_str = ""
i = start
delta = datetime.timedelta(1)	# increment by one day at a time

# construct the important parameter to the grep command
while i <= end :
  if (search_str != ""):
    search_str += "\|"
  datestr = "%d%02d%02d" % (i.year, i.month, i.day)
  search_str = search_str + "," + datestr + ","

  i = i + delta

#( command1 ; command2 ; command3 ) 
# construct and execute the grep command
#print "constructing command"

if RBNCAT == True:
# concatentate the necessary years to a separate file in /tmp;
# then we will grep that instead of the complete RBN dataset
  filename = "/tmp/extract-" + str(pid)
  
  if os.path.exists(filename):
    subprocess.call("rm " + filename, shell = True)

  for year in range(int(year_start), (int(year_end) + 1)):
    command = "rbncat " + str(year) + " >> " + filename
    subprocess.call(command, shell = True)

  command = "grep " + "'" + search_str + "' " + filename   
  
else:
  command = "grep " + "'" + search_str + "' " + data_filename

#print command

subprocess.call(command, shell = True)

#cleanup if necessary
if RBNCAT == True:
  subprocess.call("rm /tmp/extract-" + str(pid), shell = True)

