#!/usr/bin/env python3
 
# for each year from MIN_YEAR to MAX_YEAR, estimate the first "large" value of n

import math
import pandas as pd
import sys

min_year = int(sys.argv[1])
max_year = int(sys.argv[2])

UPPER_BOUND = int(sys.argv[3])
OUT_DIR = sys.argv[4]

filename = OUT_DIR + '/exact_appearances_1_' + str(UPPER_BOUND) + '.HF'

df = pd.read_csv(filename, header=None)

upper_bound = 0

for year in range(min_year, max_year + 1) :
  nr = year - min_year
  vn = df[nr]    # the V(n) values for the year

  for nm1 in range(0, len(vn) + 1 - 2) :
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

