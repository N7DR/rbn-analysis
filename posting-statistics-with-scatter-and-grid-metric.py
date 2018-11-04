#!/usr/bin/env python
# -*- coding: utf8 -*-

# posting-statistics-with-scatter-and-grid-metric.py < RBN-file [min-year [max-year]]

# produces file <base_directory>/rbn-summary-data-with-scatter-and-grid-metric, containing summary
# annual, mensal and diurnal data from a file of RBN posts. This contains the data 
# produced by posting-statistics.py AND scatter statistics AND grid-based scatter metrics.

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

from math import radians, cos, sin, asin, sqrt

import math
import os
import re
import resource
import string
import sys

resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

MIN_YEAR = 2009
MAX_YEAR = 2017

# get parameters from the command line
if len(sys.argv) == 2:
  MIN_YEAR = int(sys.argv[1])
  MAX_YEAR = MIN_YEAR
  
if len(sys.argv) > 2:
  MIN_YEAR = int(sys.argv[1])
  MAX_YEAR = int(sys.argv[2])
  
base_directory = "/tmp/rbn-data/"
  
if not os.path.isdir(base_directory):  
    os.mkdir(base_directory)

tmp_directory = "/tmp/"           # files created here are explicitly deleted later

if os.path.isdir("/zfs1/tmp"):
  tmp_directory = "/zfs1/tmp/"

# bands that we care about (everything else is "Other")
#HF_BANDS = ['160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m']
#VALID_MODES = ['CW', 'RTTY']

# define the longitudes of boundaries for G(15, 100)
cell_boundaries = [[]]  # the boundaries as function of number of cells around all longitudes

for n in xrange(0, 14):    # maximum number of cells around strip in G(15, 100) is 13
  n_cells = n + 1
  cell_width = 360.0 / (n_cells)
  this_list = []
  for cell_nr in xrange(0, n_cells):
    this_list.append(int((cell_width * cell_nr) + 0.5))
  cell_boundaries.append(this_list)

latitude_width = 15

cells_around_globe = {}
cells_around_globe[-90] = 2
cells_around_globe[-75] = 5
cells_around_globe[-60] = 8
cells_around_globe[-45] = 10
cells_around_globe[-30] = 12
cells_around_globe[-15] = 13
cells_around_globe[0] = 13
cells_around_globe[15] = 12
cells_around_globe[30] = 10
cells_around_globe[45] = 8
cells_around_globe[60] = 5
cells_around_globe[75] = 2

# get the cell indices for a particular latitude and longitude
def cell_indices(lat_long):
  latitude = lat_long[0]
  lat_index = ((int(math.floor(latitude + 90)) / latitude_width) * latitude_width) - 90
  n_cells = cells_around_globe[lat_index]
  longitude = lat_long[1]
  long_boundaries = cell_boundaries[n_cells]
  long_index = -1
  for this_boundary_nr in xrange(0, len(long_boundaries)):
    if longitude > long_boundaries[this_boundary_nr]:
      long_index += 1
      
  return [lat_index, long_index]

# https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2.0)**2 + cos(lat1) * cos(lat2) * sin(dlon/2.0)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r
  
def distance_metric(ll1, ll2):
  return haversine(ll1[1], ll1[0], ll2[1], ll2[0])

# functions for latitude and longitude
def f(z):
  return 10**(-(z-1)/2)*24**(-z/2) #this is my stroke of genius or something

# return [90, 0] if there is an error
def lat_long(grid):
  
  A=ord('A')
  
  if (ord(string.upper(grid[0]))-A > 17) or (ord(string.upper(grid[1]))-A > 17):
    return [90, 0]
  
  safety=22
  lon=lat=-90
  lets=re.findall(r'([A-Xa-x])([A-Xa-x])',grid) #slob: assume no input errors
  nums=re.findall(r'(\d)(\d)',grid)             #slob: assume no input errors
  i=tot=0
  val=range(0,safety) #sorry I don't know how to do this
    
  for m in val: #i seem to need an empty array
    val[m]=None #so so silly
    
  for x,y in lets:
    val[i*2]=(ord(string.upper(x))-A,ord(string.upper(y))-A)
    i+=1
    tot+=1
          
  i=0
    
  for x,y in nums:
    val[i*2+1]=(string.atoi(x),string.atoi(y))
    i+=1
    tot+=1
    
  i=0
    
  for x,y in val[0:min(tot,safety-1)]:
    lon += f(i-1)*x
    lat += f(i-1)*y
    i += 1
    
  lon *= 2

  return [lat, lon]

# generate day of year number from year, month and day. January 1st is doy 1.
def doy(yr, mth, day):
  start_of_month = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
  rv = start_of_month[int(mth) - 1]
  rv += (int(day) - 1)
  
  if (mth > 2) and not (yr % 4):	# handle leap year
    rv += 1
    
  return rv

# calculate scatter metric
# scatter metric is the sum of all distance pairs, divided by the number of distance pairs;
# i.e., the mean distance
def scatter_metric_1(p):
  
  scatter = 0
  
  list_posters = list(p)
	  
  if len(list_posters) < 2:
    return [0, 0, 0]
  
  count = 0
  
  for poster_index_1 in range(0, len(list_posters) - 1):
    for poster_index_2 in range(poster_index_1 + 1, len(list_posters)):
      poster_1 = list_posters[poster_index_1]
      poster_2 = list_posters[poster_index_2]

      if ( (poster_1 not in bad_posters) and (poster_2 not in bad_posters) ):
        lat_long_1 = poster_info[poster_1]
        lat_long_2 = poster_info[poster_2]

        dm = distance_metric(lat_long_1, lat_long_2)
        
        scatter += dm
        count += 1
	  
  if count == 0:
    return [0, 0, 0]
  
  good_posters = []
  
  for poster_index in range(len(list_posters)):
    poster = list_posters[poster_index]
    if (poster not in bad_posters):
      good_posters.append(poster)
  
  return [ (int(float(scatter) / count + 0.5)), len(good_posters) ]         # distance metric, number of good posters


# grid is counted only once, no matter how many times it appears in the list of posters
def grid_scatter_metric(p):  
  
  list_posters = list(p)
  
  if len(list_posters) == 0:
    return 0

  used_cells = []

  for poster in list_posters:
    if (poster not in bad_posters):
      ci = cell_indices(poster_info[poster])
      if ci not in used_cells:
	used_cells.append(ci)
	
  return len(used_cells)
      
# read the database of posters information originally from http://reversebeacon.net/nodes/#

#0: callsign 	
#1: band 	
#2: grid 	
#3: dxcc 	
#4: cont 	
#5: itu 	
#6: cq 	
#7: first seen 	
#8: last seen

database_filename = "detailed skimmers list"

# quality control seems to be a low priority for the RBN :-(
correct_grids = { 'NH6HI' : 'BL01FW',
		  'N4AX' : 'EM64OT'
		}

lines = [line.rstrip('\n') for line in open(database_filename)]
nlines = len(lines)

print_line = False

poster_info = {}

stored_callsign = ""

# put lat and long of each poster in the location database file into poster_info
for nline in xrange(0, nlines):
  line = lines[nline]
  
  if not print_line:
    if 'callsign' in line and 'band' in line:
      print_line = True
      
  if print_line:
    valid_line = ('\t' in line)
    
    if valid_line:
      fields = line.split("\t")
      callsign = fields[0].strip().upper().replace(' ', '')
      
      if ':' in callsign:
	callsign = stored_callsign
	stored_callsign = ""
      
      if 'grid' not in fields[2]:
	grid = fields[2].strip()
	
	if callsign in correct_grids:
	  grid = correct_grids[callsign]
	  	
        latlong = lat_long(grid)
        
# put longitude into range (0, 360)
        if latlong[1] < 0:
	  latlong[1] += 360
      
        if callsign not in poster_info:
	  poster_info[callsign] = latlong
    else:  # not valid line
      stored_callsign = line.strip().upper().replace(' ', '')		# probably next line will have address and port in place of this callsign

# each year has a matrix of 360 * 180 values

# list of all the known bad calls
bad_posters = ['N0CALL']

# add calls with irredeemable grid designators
for callsign in poster_info:
  if poster_info[callsign] == [90, 0]:
    bad_posters.append(callsign)

# copy stdin to a temporary file because we're going to read it for each year
pid = os.getpid()
tmp_filename = tmp_directory + "rbn-summary-data-with-scatter-and-grid-metric-tmp-" + str(pid)
outfile = open(tmp_filename, "w")

for line in sys.stdin:
  outfile.write(line)
  
outfile.close()

for YEAR in range(MIN_YEAR, MAX_YEAR + 1):				# stupid python counting
  n_posts = []		# define number of posts for each year
  spotted_calls = []      # define set of calls spotted for each year
  posters = []            # define set of posters for each year
  scatter_metrics = []    # value of scatter metric for each year

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
  for x in range(YEAR, YEAR + 1):
    n_posts.append(0)
    spotted_calls.append(set())
    posters.append(set())
  
    n_mensal_posts.append( [0 for _ in xrange(12)] )
    mensal_spotted_calls.append( [set() for _ in xrange(12)] )
    mensal_posters.append( [set() for _ in xrange(12)] )
 
    n_diurnal_posts.append( [0 for _ in xrange(366)] )
    diurnal_spotted_calls.append( [set() for _ in xrange(366)] )
    diurnal_posters.append( [set() for _ in xrange(366)] )

#for line in sys.stdin:
  with open(tmp_filename) as tmp_lines:
    for line in tmp_lines:
      fields = line.split(',')
      year = int(fields[13][0:4])
   
      if year == YEAR: 
        dx_call = fields[5].strip().upper().replace(' ', '')
        poster = fields[0].strip().upper().replace(' ', '')
        month = int(fields[13][4:6])
        day = int(fields[13][6:8])
        mode = fields[12].strip().upper().replace(' ', '')
        band = fields[4]
        
        if (poster not in poster_info) and (poster not in bad_posters):
            bad_posters.append(poster)
        
        if (poster not in posters) and (poster not in bad_posters):       # if there's no record of this being a poster in the location database
          posters.append(poster)
 
#    if band not in HF_BANDS:
#      band = 'Other'
  
# a lot of early posts had no explicit mode
        if (not mode):
          mode = "CW"
#    if mode not in VALID_MODES:
#      mode = 'Other'
 
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
      
          for x in range(YEAR, YEAR + 1):
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
      
          for x in range(YEAR, YEAR + 1):
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
	
	    for x in range(YEAR, YEAR + 1):
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
        
            for x in range(YEAR, YEAR + 1):
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

        n_posts[year - YEAR] += 1
        spotted_calls[year - YEAR].add(dx_call)
        posters[year - YEAR].add(poster)
  
        n_mensal_posts[year - YEAR][month - 1] += 1
        mensal_spotted_calls[year - YEAR][month - 1].add(dx_call)
        mensal_posters[year - YEAR][month - 1].add(poster)
 
        n_diurnal_posts[year - YEAR][day_of_year - 1] += 1
        diurnal_spotted_calls[year - YEAR][day_of_year - 1].add(dx_call)
        diurnal_posters[year - YEAR][day_of_year - 1].add(poster)
 
        n_posts_per_mode[mode][year - YEAR] += 1
        n_mensal_posts_per_mode[mode][year - YEAR][month - 1] += 1
        n_diurnal_posts_per_mode[mode][year - YEAR][day_of_year - 1] += 1
   
        spotted_calls_per_mode[mode][year - YEAR].add(dx_call)
        mensal_spotted_calls_per_mode[mode][year - YEAR][month - 1].add(dx_call)
        diurnal_spotted_calls_per_mode[mode][year - YEAR][day_of_year - 1].add(dx_call)
  
        posters_per_mode[mode][year - YEAR].add(poster) 
        mensal_posters_per_mode[mode][year - YEAR][month - 1].add(poster)
        diurnal_posters_per_mode[mode][year - YEAR][day_of_year - 1].add(poster)

        n_posts_per_band[band][year - YEAR] += 1
        n_mensal_posts_per_band[band][year - YEAR][month - 1] += 1
        n_diurnal_posts_per_band[band][year - YEAR][day_of_year - 1] += 1
    
        spotted_calls_per_band[band][year - YEAR].add(dx_call)
        mensal_spotted_calls_per_band[band][year - YEAR][month - 1].add(dx_call)
        diurnal_spotted_calls_per_band[band][year - YEAR][day_of_year - 1].add(dx_call)
   
        posters_per_band[band][year - YEAR].add(poster) 
        mensal_posters_per_band[band][year - YEAR][month - 1].add(poster)
        diurnal_posters_per_band[band][year - YEAR][day_of_year - 1].add(poster)

        n_posts_per_band_mode[band][mode][year - YEAR] += 1
        n_mensal_posts_per_band_mode[band][mode][year - YEAR][month - 1] += 1
        n_diurnal_posts_per_band_mode[band][mode][year - YEAR][day_of_year - 1] += 1

        spotted_calls_per_band_mode[band][mode][year - YEAR].add(dx_call)
        mensal_spotted_calls_per_band_mode[band][mode][year - YEAR][month - 1].add(dx_call)
        diurnal_spotted_calls_per_band_mode[band][mode][year - YEAR][day_of_year - 1].add(dx_call)

        posters_per_band_mode[band][mode][year - YEAR].add(poster)
        mensal_posters_per_band_mode[band][mode][year - YEAR][month - 1].add(poster)
        diurnal_posters_per_band_mode[band][mode][year - YEAR][day_of_year - 1].add(poster)

# create zero-length output file
  output_name = base_directory + "rbn-summary-data-with-scatter-and-grid-metric"
  
  if (MIN_YEAR == MAX_YEAR):
    output_name += "-" + str(YEAR)

  if (YEAR == MIN_YEAR):
    of = open(output_name, "w")
    of.close()

# output data in columnar format
  oformat = '{0: >14}'

#  outfile = open(base_directory + "rbn-summary-data-with-scatter-and-grid-metric-" + str(YEAR), "w")
  outfile = open(output_name, "a")

# the first line contains the column headers
  if (YEAR == MIN_YEAR):
    outfile.write( oformat.format("band") )
    outfile.write( oformat.format("mode") )
    outfile.write( oformat.format("type") )
    outfile.write( oformat.format("year") )
    outfile.write( oformat.format("month") )
    outfile.write( oformat.format("doy") )
    outfile.write( oformat.format("posts") )
    outfile.write( oformat.format("calls") )
    outfile.write( oformat.format("posters") )
    outfile.write( oformat.format("scatter") )
#    outfile.write( oformat.format("lengths") )
    outfile.write( oformat.format("good_posters") )
    outfile.write( oformat.format("grid_metric") )

    outfile.write("\n")

# Annual

  for x in range(YEAR, YEAR + 1):
    outfile.write( oformat.format("NA") )                                           # band
    outfile.write( oformat.format("NA") )                                           # mode
    outfile.write( oformat.format("A") )                                            # type = annual
    outfile.write( oformat.format(str(x)) )                                         # year
    outfile.write( oformat.format("NA") )                                           # month
    outfile.write( oformat.format("NA") )                                           # doy
    outfile.write( oformat.format(str(n_posts[x - YEAR])) )                         # posts
    outfile.write( oformat.format(str(len(spotted_calls[x - YEAR]))) )              # calls
    outfile.write( oformat.format(str(len(posters[x - YEAR]))) )                    # posters
    
    sm = scatter_metric_1(posters[x - YEAR])
    
    outfile.write( oformat.format(str(sm[0])) )                                     # distance metric
    outfile.write( oformat.format(str(sm[1])) )                                     # count
    outfile.write( oformat.format(str(grid_scatter_metric(posters[x - YEAR]))) )    # grid scatter metric
	  
    outfile.write("\n")  
  
  for x in range(YEAR, YEAR + 1):
    for mode in modes:
      outfile.write( oformat.format("NA") )                                                          # band  
      outfile.write( oformat.format(mode) )                                                          # mode  
      outfile.write( oformat.format("A") )                                                           # type = annual
      outfile.write( oformat.format(str(x)) )                                                        # year
      outfile.write( oformat.format("NA") )                                                          # month
      outfile.write( oformat.format("NA") )                                                          # doy
      outfile.write( oformat.format(str(n_posts_per_mode[mode][x - YEAR])) )                         # posts
      outfile.write( oformat.format(str(len(spotted_calls_per_mode[mode][x - YEAR]))) )              # calls
      outfile.write( oformat.format(str(len(posters_per_mode[mode][x - YEAR]))) )                    # posters

      sm = scatter_metric_1(posters_per_mode[mode][x - YEAR])

      outfile.write( oformat.format(str(sm[0])) )                                                    # distance metric
      outfile.write( oformat.format(str(sm[1])) )                                                    # count
      outfile.write( oformat.format(str(grid_scatter_metric(posters_per_mode[mode][x - YEAR]))) )    # grid scatter metric

      outfile.write("\n")  

  for x in range(YEAR, YEAR + 1):
    for band in bands:
      outfile.write( oformat.format(band) )                                                          # band  
      outfile.write( oformat.format("NA") )                                                          # mode  
      outfile.write( oformat.format("A") )                                                           # type = annual
      outfile.write( oformat.format(str(x)) )                                                        # year
      outfile.write( oformat.format("NA") )                                                          # month
      outfile.write( oformat.format("NA") )                                                          # doy
      outfile.write( oformat.format(str(n_posts_per_band[band][x - YEAR])) )                         # posts
      outfile.write( oformat.format(str(len(spotted_calls_per_band[band][x - YEAR]))) )              # calls
      outfile.write( oformat.format(str(len(posters_per_band[band][x - YEAR]))) )                    # posters

      sm = scatter_metric_1(posters_per_band[band][x - YEAR])

      outfile.write( oformat.format(str(sm[0])) )                                                    # distance metric
      outfile.write( oformat.format(str(sm[1])) )                                                    # count
      outfile.write( oformat.format(str(grid_scatter_metric(posters_per_band[band][x - YEAR]))) )    # grid scatter metric

      outfile.write("\n")  

  for x in range(YEAR, YEAR + 1):
    for band in bands:
      for mode in modes:
        outfile.write( oformat.format(band) )                                                                    # band  
        outfile.write( oformat.format(mode) )                                                                    # mode  
        outfile.write( oformat.format("A") )                                                                     # type = annual
        outfile.write( oformat.format(str(x)) )                                                                  # year
        outfile.write( oformat.format("NA") )                                                                    # month
        outfile.write( oformat.format("NA") )                                                                    # doy
        outfile.write( oformat.format(str(n_posts_per_band_mode[band][mode][x - YEAR])) )                        # posts
        outfile.write( oformat.format(str(len(spotted_calls_per_band_mode[band][mode][x - YEAR]))) )             # calls
        outfile.write( oformat.format(str(len(posters_per_band_mode[band][mode][x - YEAR]))) )                   # posters

        sm = scatter_metric_1(posters_per_band_mode[band][mode][x - YEAR])

        outfile.write( oformat.format(str(sm[0])) )                                                              # distance metric 
        outfile.write( oformat.format(str(sm[1])) )                                                              # count
        outfile.write( oformat.format(str(grid_scatter_metric(posters_per_band_mode[band][mode][x - YEAR]))) )   # grid scatter metric

        outfile.write("\n")  

# Mensal

  for x in range(YEAR, YEAR + 1):
    for month in range(0, 12):
      outfile.write( oformat.format("NA") )                                                             # band
      outfile.write( oformat.format("NA") )                                                             # mode
      outfile.write( oformat.format("M") )                                                              # type = mensal
      outfile.write( oformat.format(str(x)) )                                                           # year
      outfile.write( oformat.format(month + 1) )                                                        # month
      outfile.write( oformat.format("NA") )                                                             # doy
      outfile.write( oformat.format(str(n_mensal_posts[x - YEAR][month])) )                             # posts
      outfile.write( oformat.format(str(len(mensal_spotted_calls[x - YEAR][month]))) )                  # calls
      outfile.write( oformat.format(str(len(mensal_posters[x - YEAR][month]))) )                        # posters

      sm = scatter_metric_1(mensal_posters[x - YEAR][month])

      outfile.write( oformat.format(str(sm[0])) )                                                       # distance metric
      outfile.write( oformat.format(str(sm[1])) )                                                       # count
      outfile.write( oformat.format(str(grid_scatter_metric(mensal_posters[x - YEAR][month]))) )        # grid scatter metric

      outfile.write("\n")  

  for x in range(YEAR, YEAR + 1):
    for mode in modes:
      for month in range(0, 12):
        outfile.write( oformat.format("NA") )                                                                        # band
        outfile.write( oformat.format(mode) )                                                                        # mode
        outfile.write( oformat.format("M") )                                                                         # type = mensal
        outfile.write( oformat.format(str(x)) )                                                                      # year
        outfile.write( oformat.format(month + 1) )                                                                   # month
        outfile.write( oformat.format("NA") )                                                                        # doy
        outfile.write( oformat.format(str(n_mensal_posts_per_mode[mode][x - YEAR][month])) )                         # posts
        outfile.write( oformat.format(str(len(mensal_spotted_calls_per_mode[mode][x - YEAR][month]))) )              # calls
        outfile.write( oformat.format(str(len(mensal_posters_per_mode[mode][x - YEAR][month]))) )                    # posters

        sm = scatter_metric_1(mensal_posters_per_mode[mode][x - YEAR][month])

        outfile.write( oformat.format(str(sm[0])) )                                                                  # distance metric
        outfile.write( oformat.format(str(sm[1])) )                                                                  # count
        outfile.write( oformat.format(str(grid_scatter_metric(mensal_posters_per_mode[mode][x - YEAR][month]))) )    # grid scatter metric

        outfile.write("\n")  

  for x in range(YEAR, YEAR + 1):
    for band in bands:
      for month in range(0, 12):
        outfile.write( oformat.format(band) )                                                                        # band
        outfile.write( oformat.format("NA") )                                                                        # mode
        outfile.write( oformat.format("M") )                                                                         # type = mensal
        outfile.write( oformat.format(str(x)) )                                                                      # year
        outfile.write( oformat.format(month + 1) )                                                                   # month
        outfile.write( oformat.format("NA") )                                                                        # doy
        outfile.write( oformat.format(str(n_mensal_posts_per_band[band][x - YEAR][month])) )                         # posts
        outfile.write( oformat.format(str(len(mensal_spotted_calls_per_band[band][x - YEAR][month]))) )              # calls
        outfile.write( oformat.format(str(len(mensal_posters_per_band[band][x - YEAR][month]))) )                    # posters

        sm = scatter_metric_1(mensal_posters_per_band[band][x - YEAR][month])

        outfile.write( oformat.format(str(sm[0])) )                                                                  # distance metric
        outfile.write( oformat.format(str(sm[1])) )                                                                  # count
        outfile.write( oformat.format(str(grid_scatter_metric(mensal_posters_per_band[band][x - YEAR][month]))) )    # grid scatter metric

        outfile.write("\n")  

  for x in range(YEAR, YEAR + 1):
    for band in bands:
      for mode in modes:
        for month in range(0, 12):
          outfile.write( oformat.format(band) )                                                                                   # band
          outfile.write( oformat.format(mode) )                                                                                   # mode
          outfile.write( oformat.format("M") )                                                                                    # type = mensal
          outfile.write( oformat.format(str(x)) )                                                                                 # year
          outfile.write( oformat.format(month + 1) )                                                                              # month
          outfile.write( oformat.format("NA") )                                                                                   # doy
          outfile.write( oformat.format(str(n_mensal_posts_per_band_mode[band][mode][x - YEAR][month])) )                         # posts
          outfile.write( oformat.format(str(len(mensal_spotted_calls_per_band_mode[band][mode][x - YEAR][month]))) )              # calls
          outfile.write( oformat.format(str(len(mensal_posters_per_band_mode[band][mode][x - YEAR][month]))) )                    # posters

          sm = scatter_metric_1(mensal_posters_per_band_mode[band][mode][x - YEAR][month])

          outfile.write( oformat.format(str(sm[0])) )                                                                             # distance metric
          outfile.write( oformat.format(str(sm[1])) )                                                                             # count
          outfile.write( oformat.format(str(grid_scatter_metric(mensal_posters_per_band_mode[band][mode][x - YEAR][month]))) )    # grid scatter metric

          outfile.write("\n")  

# Diurnal

  for x in range(YEAR, YEAR + 1):
    for day_number in range(0, 366):
      outfile.write( oformat.format("NA") )                                                             # band
      outfile.write( oformat.format("NA") )                                                             # mode
      outfile.write( oformat.format("D") )                                                              # type = diurnal
      outfile.write( oformat.format(str(x)) )                                                           # year
      outfile.write( oformat.format("NA") )                                                             # month
      outfile.write( oformat.format(day_number + 1) )                                                   # doy
      outfile.write( oformat.format(str(n_diurnal_posts[x - YEAR][day_number])) )                       # posts
      outfile.write( oformat.format(str(len(diurnal_spotted_calls[x - YEAR][day_number]))) )            # calls
      outfile.write( oformat.format(str(len(diurnal_posters[x - YEAR][day_number]))) )                  # posters

      sm = scatter_metric_1(diurnal_posters[x - YEAR][day_number])

      outfile.write( oformat.format(str(sm[0])) )                                                       # distance metric
      outfile.write( oformat.format(str(sm[1])) )                                                       # count
      outfile.write( oformat.format(str(grid_scatter_metric(diurnal_posters[x - YEAR][day_number]))) )  # grid scatter metric

      outfile.write("\n")  

  for x in range(YEAR, YEAR + 1):
    for mode in modes:
      for day_number in range(0, 366):
        outfile.write( oformat.format("NA") )                                                                            # band
        outfile.write( oformat.format(mode) )                                                                            # mode
        outfile.write( oformat.format("D") )                                                                             # type = diurnal
        outfile.write( oformat.format(str(x)) )                                                                          # year
        outfile.write( oformat.format("NA") )                                                                            # month
        outfile.write( oformat.format(day_number + 1) )                                                                  # doy
        outfile.write( oformat.format(str(n_diurnal_posts_per_mode[mode][x - YEAR][day_number])) )                       # posts
        outfile.write( oformat.format(str(len(diurnal_spotted_calls_per_mode[mode][x - YEAR][day_number]))) )            # calls
        outfile.write( oformat.format(str(len(diurnal_posters_per_mode[mode][x - YEAR][day_number]))) )                  # posters

        sm = scatter_metric_1(diurnal_posters_per_mode[mode][x - YEAR][day_number])

        outfile.write( oformat.format(str(sm[0])) )                                                                      # distance metric
        outfile.write( oformat.format(str(sm[1])) )                                                                      # count
        outfile.write( oformat.format(str(grid_scatter_metric(diurnal_posters_per_mode[mode][x - YEAR][day_number]))) )  # grid scatter metric

        outfile.write("\n")  

  for x in range(YEAR, YEAR + 1):
    for band in bands:
      for day_number in range(0, 366):
        outfile.write( oformat.format(band) )                                                                             # band
        outfile.write( oformat.format("NA") )                                                                             # mode
        outfile.write( oformat.format("D") )                                                                              # type = diurnal
        outfile.write( oformat.format(str(x)) )                                                                           # year
        outfile.write( oformat.format("NA") )                                                                             # month
        outfile.write( oformat.format(day_number + 1) )                                                                   # doy
        outfile.write( oformat.format(str(n_diurnal_posts_per_band[band][x - YEAR][day_number])) )                        # posts
        outfile.write( oformat.format(str(len(diurnal_spotted_calls_per_band[band][x - YEAR][day_number]))) )             # calls
        outfile.write( oformat.format(str(len(diurnal_posters_per_band[band][x - YEAR][day_number]))) )                   # posters

        sm = scatter_metric_1(diurnal_posters_per_band[band][x - YEAR][day_number])

        outfile.write( oformat.format(str(sm[0])) )                                                                       # distance metric
        outfile.write( oformat.format(str(sm[1])) )                                                                       # count
        outfile.write( oformat.format(str(grid_scatter_metric(diurnal_posters_per_band[band][x - YEAR][day_number]))) )   # grid scatter metric

        outfile.write("\n")  

  for x in range(YEAR, YEAR + 1):
    for band in bands:
      for mode in modes:
        for day_number in range(0, 366):
          outfile.write( oformat.format(band) )                                                                                       # band
          outfile.write( oformat.format(mode) )                                                                                       # mode
          outfile.write( oformat.format("D") )                                                                                        # type = diurnal
          outfile.write( oformat.format(str(x)) )                                                                                     # year
          outfile.write( oformat.format("NA") )                                                                                       # month
          outfile.write( oformat.format(day_number + 1) )                                                                             # doy
          outfile.write( oformat.format(str(n_diurnal_posts_per_band_mode[band][mode][x - YEAR][day_number])) )                       # posts
          outfile.write( oformat.format(str(len(diurnal_spotted_calls_per_band_mode[band][mode][x - YEAR][day_number]))) )            # calls
          outfile.write( oformat.format(str(len(diurnal_posters_per_band_mode[band][mode][x - YEAR][day_number]))) )                  # posters

          sm = scatter_metric_1(diurnal_posters_per_band_mode[band][mode][x - YEAR][day_number])

          outfile.write( oformat.format(str(sm[0])) )                                                                                 # distance metric
          outfile.write( oformat.format(str(sm[1])) )                                                                                 # count
          outfile.write( oformat.format(str(grid_scatter_metric(diurnal_posters_per_band_mode[band][mode][x - YEAR][day_number]))) )  # grid scatter metric

          outfile.write("\n")  

  outfile.close()

# delete the temporary file
os.remove(tmp_filename)
