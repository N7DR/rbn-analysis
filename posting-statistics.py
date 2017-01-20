#!/usr/bin/env python
# -*- coding: utf8 -*-

# posting-statistics.py < RBN-file

# produces file <base_directory>/rbn-summary-data, containing summary
# annual, mensal and diurnal data

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

import sys

MIN_YEAR = 2009
MAX_YEAR = 2016

base_directory = "/tmp/rbn-data/"

# generate day of year number from year, month and day. January 1st is doy 1.
def doy(yr, mth, day):
  start_of_month = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
  rv = start_of_month[int(mth) - 1]
  rv += (int(day) - 1)
  
  if (mth > 2) and not (yr % 4):	# handle leap year
    rv += 1
    
  return rv

n_posts = []		# define number of posts for each year
spotted_calls = []      # define number of calls spotted for each year
posters = []            # define number of posters for each year

# clear modes and bands
modes = set()
bands = set()

# clear mensal values
n_mensal_posts = []
mensal_spotted_calls = []
mensal_posters = []

# clear diurnal values
n_diurnal_posts = []
diurnal_spotted_calls = []
diurnal_posters = []

# clear values per mode
n_posts_per_mode = {}
n_mensal_posts_per_mode = {}
n_diurnal_posts_per_mode = {}

spotted_calls_per_mode = {}
mensal_spotted_calls_per_mode = {}
diurnal_spotted_calls_per_mode = {}

posters_per_mode = {}
mensal_posters_per_mode = {}
diurnal_posters_per_mode = {}

# clear values per band
n_posts_per_band = {}
n_mensal_posts_per_band = {}
n_diurnal_posts_per_band = {}

spotted_calls_per_band = {}
mensal_spotted_calls_per_band = {}
diurnal_spotted_calls_per_band = {}

posters_per_band = {}
mensal_posters_per_band = {}
diurnal_posters_per_band = {}

# clear values per band and mode
n_posts_per_band_mode = {}
n_mensal_posts_per_band_mode = {}
n_diurnal_posts_per_band_mode = {}

spotted_calls_per_band_mode = {}
mensal_spotted_calls_per_band_mode = {}
diurnal_spotted_calls_per_band_mode = {}

posters_per_band_mode = {}
mensal_posters_per_band_mode = {}
diurnal_posters_per_band_mode = {}

# initialise a bunch of values
for x in range(MIN_YEAR, MAX_YEAR + 1):
  n_posts.append(0)
  spotted_calls.append(set())
  posters.append(set())
  
  n_mensal_posts.append( [0 for _ in xrange(12)] )
  mensal_spotted_calls.append( [set() for _ in xrange(12)] )
  mensal_posters.append( [set() for _ in xrange(12)] )
 
  n_diurnal_posts.append( [0 for _ in xrange(366)] )
  diurnal_spotted_calls.append( [set() for _ in xrange(366)] )
  diurnal_posters.append( [set() for _ in xrange(366)] )

for line in sys.stdin:
  fields = line.split(',')
  year = int(fields[13][0:4])
  
  if year >= MIN_YEAR and year <= MAX_YEAR: 
    dx_call = fields[5]
    poster = fields[0]
    month = int(fields[13][4:6])
    day = int(fields[13][6:8])
    mode = fields[12]
    band = fields[4]
  
# a lot of early posts had no explicit mode
    if (not mode):
      mode = "CW"
 
    new_band = (band not in bands)
    new_mode = (mode not in modes)
 
    if new_mode:
      n_posts_per_mode[mode] = []
      n_mensal_posts_per_mode[mode] = []      
      n_diurnal_posts_per_mode[mode] = []

      spotted_calls_per_mode[mode] = []
      mensal_spotted_calls_per_mode[mode] = []
      diurnal_spotted_calls_per_mode[mode] = []

      posters_per_mode[mode] = []
      mensal_posters_per_mode[mode] = []
      diurnal_posters_per_mode[mode] = []
      
      for x in range(MIN_YEAR, MAX_YEAR + 1):
        n_posts_per_mode[mode].append(0) 
        n_mensal_posts_per_mode[mode].append( [0 for _ in xrange(12)] ) 
        n_diurnal_posts_per_mode[mode].append( [0 for _ in xrange(366)] ) 
 
        spotted_calls_per_mode[mode].append(set())  
        mensal_spotted_calls_per_mode[mode].append( [set() for _ in xrange(12)] )
        diurnal_spotted_calls_per_mode[mode].append( [set() for _ in xrange(366)] )

        posters_per_mode[mode].append(set())
        mensal_posters_per_mode[mode].append( [set() for _ in xrange(12)] )
        diurnal_posters_per_mode[mode].append( [set() for _ in xrange(366)] )

    if new_band:
      n_posts_per_band[band] = []
      n_mensal_posts_per_band[band] = []
      n_diurnal_posts_per_band[band] = []

      spotted_calls_per_band[band] = []
      mensal_spotted_calls_per_band[band] = []
      diurnal_spotted_calls_per_band[band] = []

      posters_per_band[band] = []
      mensal_posters_per_band[band] = []
      diurnal_posters_per_band[band] = []
      
      for x in range(MIN_YEAR, MAX_YEAR + 1):
        n_posts_per_band[band].append(0)
        n_mensal_posts_per_band[band].append( [0 for _ in xrange(12)] )
        n_diurnal_posts_per_band[band].append( [0 for _ in xrange(366)] )

        spotted_calls_per_band[band].append(set())
        mensal_spotted_calls_per_band[band].append( [set() for _ in xrange(12)] )
        diurnal_spotted_calls_per_band[band].append( [set() for _ in xrange(366)] )
 
        posters_per_band[band].append(set())
        mensal_posters_per_band[band].append( [set() for _ in xrange(12)] )
        diurnal_posters_per_band[band].append( [set() for _ in xrange(366)] )

    if new_band:
      n_posts_per_band_mode[band] = {}
      n_mensal_posts_per_band_mode[band] = {}
      n_diurnal_posts_per_band_mode[band] = {}

      spotted_calls_per_band_mode[band] = {}
      mensal_spotted_calls_per_band_mode[band] = {}
      diurnal_spotted_calls_per_band_mode[band] = {}
      
      posters_per_band_mode[band] = {}
      mensal_posters_per_band_mode[band] = {}
      diurnal_posters_per_band_mode[band] = {}
       
      known_modes = modes
      known_modes.add(mode)
      
      for known_mode in known_modes:
	n_posts_per_band_mode[band][known_mode] = []
        n_mensal_posts_per_band_mode[band][known_mode] = []
	n_diurnal_posts_per_band_mode[band][known_mode] = []
	
        spotted_calls_per_band_mode[band][known_mode] = []
	mensal_spotted_calls_per_band_mode[band][known_mode] = []
	diurnal_spotted_calls_per_band_mode[band][known_mode] = []
	
	posters_per_band_mode[band][known_mode] = []
	mensal_posters_per_band_mode[band][known_mode] = []
	diurnal_posters_per_band_mode[band][known_mode] = []
	
	for x in range(MIN_YEAR, MAX_YEAR + 1):
          n_posts_per_band_mode[band][known_mode].append(0)
          n_mensal_posts_per_band_mode[band][known_mode].append( [0 for _ in xrange(12)] )
          n_diurnal_posts_per_band_mode[band][known_mode].append( [0 for _ in xrange(366)] )

          spotted_calls_per_band_mode[band][known_mode].append(set())
          mensal_spotted_calls_per_band_mode[band][known_mode].append( [ set() for _ in xrange(12) ] )
          diurnal_spotted_calls_per_band_mode[band][known_mode].append( [ set() for _ in xrange(366) ] )
          
          posters_per_band_mode[band][known_mode].append(set())
          mensal_posters_per_band_mode[band][known_mode].append( [ set() for _ in xrange(12) ] )
          diurnal_posters_per_band_mode[band][known_mode].append( [ set() for _ in xrange(366) ] )
        
    if new_mode:
      known_bands = bands
      known_bands.add(band)
      
      for known_band in known_bands:
        n_posts_per_band_mode[known_band][mode] = []
        n_mensal_posts_per_band_mode[known_band][mode] = []       
        n_diurnal_posts_per_band_mode[known_band][mode] = []

        spotted_calls_per_band_mode[known_band][mode] = []
        mensal_spotted_calls_per_band_mode[known_band][mode] = []
        diurnal_spotted_calls_per_band_mode[known_band][mode] = []
        
        posters_per_band_mode[known_band][mode] = []
        mensal_posters_per_band_mode[known_band][mode] = []
        diurnal_posters_per_band_mode[known_band][mode] = []
        
        for x in range(MIN_YEAR, MAX_YEAR + 1):
          n_posts_per_band_mode[known_band][mode].append(0)
          n_mensal_posts_per_band_mode[known_band][mode].append( [0 for _ in xrange(12)] )
          n_diurnal_posts_per_band_mode[known_band][mode].append( [0 for _ in xrange(366)] )

          spotted_calls_per_band_mode[known_band][mode].append(set())
	  mensal_spotted_calls_per_band_mode[known_band][mode].append( [ set() for _ in xrange(12) ] )
	  diurnal_spotted_calls_per_band_mode[known_band][mode].append( [ set() for _ in xrange(366) ] )

          posters_per_band_mode[known_band][mode].append(set())
	  mensal_posters_per_band_mode[known_band][mode].append( [ set() for _ in xrange(12) ] )
	  diurnal_posters_per_band_mode[known_band][mode].append( [ set() for _ in xrange(366) ] )

    modes.add(mode)
    bands.add(band)
    
    day_of_year = doy(year, month, day)

    n_posts[year - MIN_YEAR] += 1
    spotted_calls[year - MIN_YEAR].add(dx_call)
    posters[year - MIN_YEAR].add(poster)
  
    n_mensal_posts[year - MIN_YEAR][month - 1] += 1
    mensal_spotted_calls[year - MIN_YEAR][month - 1].add(dx_call)
    mensal_posters[year - MIN_YEAR][month - 1].add(poster)
 
    n_diurnal_posts[year - MIN_YEAR][day_of_year - 1] += 1
    diurnal_spotted_calls[year - MIN_YEAR][day_of_year - 1].add(dx_call)
    diurnal_posters[year - MIN_YEAR][day_of_year - 1].add(poster)
 
    n_posts_per_mode[mode][year - MIN_YEAR] += 1
    n_mensal_posts_per_mode[mode][year - MIN_YEAR][month - 1] += 1
    n_diurnal_posts_per_mode[mode][year - MIN_YEAR][day_of_year - 1] += 1
   
    spotted_calls_per_mode[mode][year - MIN_YEAR].add(dx_call)
    mensal_spotted_calls_per_mode[mode][year - MIN_YEAR][month - 1].add(dx_call)
    diurnal_spotted_calls_per_mode[mode][year - MIN_YEAR][day_of_year - 1].add(dx_call)
  
    posters_per_mode[mode][year - MIN_YEAR].add(poster) 
    mensal_posters_per_mode[mode][year - MIN_YEAR][month - 1].add(poster)
    diurnal_posters_per_mode[mode][year - MIN_YEAR][day_of_year - 1].add(poster)

    n_posts_per_band[band][year - MIN_YEAR] += 1
    n_mensal_posts_per_band[band][year - MIN_YEAR][month - 1] += 1
    n_diurnal_posts_per_band[band][year - MIN_YEAR][day_of_year - 1] += 1
    
    spotted_calls_per_band[band][year - MIN_YEAR].add(dx_call)
    mensal_spotted_calls_per_band[band][year - MIN_YEAR][month - 1].add(dx_call)
    diurnal_spotted_calls_per_band[band][year - MIN_YEAR][day_of_year - 1].add(dx_call)
   
    posters_per_band[band][year - MIN_YEAR].add(poster) 
    mensal_posters_per_band[band][year - MIN_YEAR][month - 1].add(poster)
    diurnal_posters_per_band[band][year - MIN_YEAR][day_of_year - 1].add(poster)

    n_posts_per_band_mode[band][mode][year - MIN_YEAR] += 1
    n_mensal_posts_per_band_mode[band][mode][year - MIN_YEAR][month - 1] += 1
    n_diurnal_posts_per_band_mode[band][mode][year - MIN_YEAR][day_of_year - 1] += 1

    spotted_calls_per_band_mode[band][mode][year - MIN_YEAR].add(dx_call)
    mensal_spotted_calls_per_band_mode[band][mode][year - MIN_YEAR][month - 1].add(dx_call)
    diurnal_spotted_calls_per_band_mode[band][mode][year - MIN_YEAR][day_of_year - 1].add(dx_call)

    posters_per_band_mode[band][mode][year - MIN_YEAR].add(poster)
    mensal_posters_per_band_mode[band][mode][year - MIN_YEAR][month - 1].add(poster)
    diurnal_posters_per_band_mode[band][mode][year - MIN_YEAR][day_of_year - 1].add(poster)

# output data in columnar format
oformat = '{0: >14}'

outfile = open(base_directory + "rbn-summary-data", "w")

# the first line contains the column headers
outfile.write( oformat.format("band") )
outfile.write( oformat.format("mode") )
outfile.write( oformat.format("type") )
outfile.write( oformat.format("year") )
outfile.write( oformat.format("month") )
outfile.write( oformat.format("doy") )
outfile.write( oformat.format("posts") )
outfile.write( oformat.format("calls") )
outfile.write( oformat.format("posters") )

outfile.write("\n")

# Annual

for x in range(MIN_YEAR, MAX_YEAR + 1):
  outfile.write( oformat.format("NA") )                                   # band
  outfile.write( oformat.format("NA") )                                   # mode
  outfile.write( oformat.format("A") )                                    # type = annual
  outfile.write( oformat.format(str(x)) )                                 # year
  outfile.write( oformat.format("NA") )                                   # month
  outfile.write( oformat.format("NA") )                                   # doy
  outfile.write( oformat.format(str(n_posts[x - MIN_YEAR])) )             # posts
  outfile.write( oformat.format(str(len(spotted_calls[x - MIN_YEAR]))) )  # calls
  outfile.write( oformat.format(str(len(posters[x - MIN_YEAR]))) )        # posters

  outfile.write("\n")  
  
for x in range(MIN_YEAR, MAX_YEAR + 1):
  for mode in modes:
    outfile.write( oformat.format("NA") )                                                  # band  
    outfile.write( oformat.format(mode) )                                                  # mode  
    outfile.write( oformat.format("A") )                                                   # type = annual
    outfile.write( oformat.format(str(x)) )                                                # year
    outfile.write( oformat.format("NA") )                                                  # month
    outfile.write( oformat.format("NA") )                                                  # doy
    outfile.write( oformat.format(str(n_posts_per_mode[mode][x - MIN_YEAR])) )             # posts
    outfile.write( oformat.format(str(len(spotted_calls_per_mode[mode][x - MIN_YEAR]))) )  # calls
    outfile.write( oformat.format(str(len(posters_per_mode[mode][x - MIN_YEAR]))) )        # posters

    outfile.write("\n")  

for x in range(MIN_YEAR, MAX_YEAR + 1):
  for band in bands:
    outfile.write( oformat.format(band) )                                                  # band  
    outfile.write( oformat.format("NA") )                                                  # mode  
    outfile.write( oformat.format("A") )                                                   # type = annual
    outfile.write( oformat.format(str(x)) )                                                # year
    outfile.write( oformat.format("NA") )                                                  # month
    outfile.write( oformat.format("NA") )                                                  # doy
    outfile.write( oformat.format(str(n_posts_per_band[band][x - MIN_YEAR])) )             # posts
    outfile.write( oformat.format(str(len(spotted_calls_per_band[band][x - MIN_YEAR]))) )  # calls
    outfile.write( oformat.format(str(len(posters_per_band[band][x - MIN_YEAR]))) )        # posters

    outfile.write("\n")  

for x in range(MIN_YEAR, MAX_YEAR + 1):
  for band in bands:
    for mode in modes:
      outfile.write( oformat.format(band) )                                                             # band  
      outfile.write( oformat.format(mode) )                                                             # mode  
      outfile.write( oformat.format("A") )                                                              # type = annual
      outfile.write( oformat.format(str(x)) )                                                           # year
      outfile.write( oformat.format("NA") )                                                             # month
      outfile.write( oformat.format("NA") )                                                             # doy
      outfile.write( oformat.format(str(n_posts_per_band_mode[band][mode][x - MIN_YEAR])) )             # posts
      outfile.write( oformat.format(str(len(spotted_calls_per_band_mode[band][mode][x - MIN_YEAR]))) )  # calls
      outfile.write( oformat.format(str(len(posters_per_band_mode[band][mode][x - MIN_YEAR]))) )        # posters

      outfile.write("\n")  

# Mensal

for x in range(MIN_YEAR, MAX_YEAR + 1):
  for month in range(0, 12):
    outfile.write( oformat.format("NA") )                                                 # band
    outfile.write( oformat.format("NA") )                                                 # mode
    outfile.write( oformat.format("M") )                                                  # type = mensal
    outfile.write( oformat.format(str(x)) )                                               # year
    outfile.write( oformat.format(month + 1) )                                            # month
    outfile.write( oformat.format("NA") )                                                 # doy
    outfile.write( oformat.format(str(n_mensal_posts[x - MIN_YEAR][month])) )             # posts
    outfile.write( oformat.format(str(len(mensal_spotted_calls[x - MIN_YEAR][month]))) )  # calls
    outfile.write( oformat.format(str(len(mensal_posters[x - MIN_YEAR][month]))) )        # posters

    outfile.write("\n")  

for x in range(MIN_YEAR, MAX_YEAR + 1):
  for mode in modes:
    for month in range(0, 12):
      outfile.write( oformat.format("NA") )                                                                # band
      outfile.write( oformat.format(mode) )                                                                # mode
      outfile.write( oformat.format("M") )                                                                 # type = mensal
      outfile.write( oformat.format(str(x)) )                                                              # year
      outfile.write( oformat.format(month + 1) )                                                           # month
      outfile.write( oformat.format("NA") )                                                                # doy
      outfile.write( oformat.format(str(n_mensal_posts_per_mode[mode][x - MIN_YEAR][month])) )             # posts
      outfile.write( oformat.format(str(len(mensal_spotted_calls_per_mode[mode][x - MIN_YEAR][month]))) )  # calls
      outfile.write( oformat.format(str(len(mensal_posters_per_mode[mode][x - MIN_YEAR][month]))) )        # posters

      outfile.write("\n")  

for x in range(MIN_YEAR, MAX_YEAR + 1):
  for band in bands:
    for month in range(0, 12):
      outfile.write( oformat.format(band) )                                                                # band
      outfile.write( oformat.format("NA") )                                                                # mode
      outfile.write( oformat.format("M") )                                                                 # type = mensal
      outfile.write( oformat.format(str(x)) )                                                              # year
      outfile.write( oformat.format(month + 1) )                                                           # month
      outfile.write( oformat.format("NA") )                                                                # doy
      outfile.write( oformat.format(str(n_mensal_posts_per_band[band][x - MIN_YEAR][month])) )             # posts
      outfile.write( oformat.format(str(len(mensal_spotted_calls_per_band[band][x - MIN_YEAR][month]))) )  # calls
      outfile.write( oformat.format(str(len(mensal_posters_per_band[band][x - MIN_YEAR][month]))) )        # posters

      outfile.write("\n")  

for x in range(MIN_YEAR, MAX_YEAR + 1):
  for band in bands:
    for mode in modes:
      for month in range(0, 12):
        outfile.write( oformat.format(band) )                                                                           # band
        outfile.write( oformat.format(mode) )                                                                           # mode
        outfile.write( oformat.format("M") )                                                                            # type = mensal
        outfile.write( oformat.format(str(x)) )                                                                         # year
        outfile.write( oformat.format(month + 1) )                                                                      # month
        outfile.write( oformat.format("NA") )                                                                           # doy
        outfile.write( oformat.format(str(n_mensal_posts_per_band_mode[band][mode][x - MIN_YEAR][month])) )             # posts
        outfile.write( oformat.format(str(len(mensal_spotted_calls_per_band_mode[band][mode][x - MIN_YEAR][month]))) )  # calls
        outfile.write( oformat.format(str(len(mensal_posters_per_band_mode[band][mode][x - MIN_YEAR][month]))) )        # posters

        outfile.write("\n")  

# Diurnal

for x in range(MIN_YEAR, MAX_YEAR + 1):
  for doy in range(0, 366):
    outfile.write( oformat.format("NA") )                                                 # band
    outfile.write( oformat.format("NA") )                                                 # mode
    outfile.write( oformat.format("D") )                                                  # type = diurnal
    outfile.write( oformat.format(str(x)) )                                               # year
    outfile.write( oformat.format("NA") )                                                 # month
    outfile.write( oformat.format(doy + 1) )                                              # doy
    outfile.write( oformat.format(str(n_diurnal_posts[x - MIN_YEAR][doy])) )              # posts
    outfile.write( oformat.format(str(len(diurnal_spotted_calls[x - MIN_YEAR][doy]))) )   # calls
    outfile.write( oformat.format(str(len(diurnal_posters[x - MIN_YEAR][doy]))) )         # posters

    outfile.write("\n")  

for x in range(MIN_YEAR, MAX_YEAR + 1):
  for mode in modes:
    for doy in range(0, 366):
      outfile.write( oformat.format("NA") )                                                                # band
      outfile.write( oformat.format(mode) )                                                                # mode
      outfile.write( oformat.format("D") )                                                                 # type = diurnal
      outfile.write( oformat.format(str(x)) )                                                              # year
      outfile.write( oformat.format("NA") )                                                                # month
      outfile.write( oformat.format(doy + 1) )                                                             # doy
      outfile.write( oformat.format(str(n_diurnal_posts_per_mode[mode][x - MIN_YEAR][doy])) )              # posts
      outfile.write( oformat.format(str(len(diurnal_spotted_calls_per_mode[mode][x - MIN_YEAR][doy]))) )   # calls
      outfile.write( oformat.format(str(len(diurnal_posters_per_mode[mode][x - MIN_YEAR][doy]))) )         # posters

      outfile.write("\n")  

for x in range(MIN_YEAR, MAX_YEAR + 1):
  for band in bands:
    for doy in range(0, 366):
      outfile.write( oformat.format(band) )                                                               # band
      outfile.write( oformat.format("NA") )                                                               # mode
      outfile.write( oformat.format("D") )                                                                # type = diurnal
      outfile.write( oformat.format(str(x)) )                                                             # year
      outfile.write( oformat.format("NA") )                                                               # month
      outfile.write( oformat.format(doy + 1) )                                                            # doy
      outfile.write( oformat.format(str(n_diurnal_posts_per_band[band][x - MIN_YEAR][doy])) )             # posts
      outfile.write( oformat.format(str(len(diurnal_spotted_calls_per_band[band][x - MIN_YEAR][doy]))) )  # calls
      outfile.write( oformat.format(str(len(diurnal_posters_per_band[band][x - MIN_YEAR][doy]))) )        # posters

      outfile.write("\n")  

for x in range(MIN_YEAR, MAX_YEAR + 1):
  for band in bands:
    for mode in modes:
      for doy in range(0, 366):
        outfile.write( oformat.format(band) )                                                                          # band
        outfile.write( oformat.format(mode) )                                                                          # mode
        outfile.write( oformat.format("D") )                                                                           # type = diurnal
        outfile.write( oformat.format(str(x)) )                                                                        # year
        outfile.write( oformat.format("NA") )                                                                          # month
        outfile.write( oformat.format(doy + 1) )                                                                       # doy
        outfile.write( oformat.format(str(n_diurnal_posts_per_band_mode[band][mode][x - MIN_YEAR][doy])) )             # posts
        outfile.write( oformat.format(str(len(diurnal_spotted_calls_per_band_mode[band][mode][x - MIN_YEAR][doy]))) )  # calls
        outfile.write( oformat.format(str(len(diurnal_posters_per_band_mode[band][mode][x - MIN_YEAR][doy]))) )        # posters

        outfile.write("\n")  

outfile.close()

