#! /bin/sh

# this is all very inefficient compared to a dedicated program, which would
# probably run between one and two orders of magnitude more quickly (I'm guessing). 
# But this is much simpler and should run pretty much anywhere without the need to
# build an executable.

export MIN_YEAR=2009
export MAX_YEAR=2020

export OUT_DIR='/tmp/cwa'

# it's stupid that I can't run at j-1, but the temp sensor beeps if I do
export N_JOBS='-j-2'

mkdir -p $OUT_DIR

# extract CW data for bands and years from the RBN dataset
# this assumes the presence of the rbncat command:
#   rbncat <year> extracts and writes all the RBN data for the named year to stdout
./job1.sh

# get the total number of posts for each year and band
sem --id $$ $N_JOBS ./job2.sh

# get the total number of different calls posted for each year and band
sem --id $$ $N_JOBS ./job3.sh

sem --id $$ --wait

# for each year, get the number of calls that appear 1, 2, 3, ... 100 times
./job4.sh 100

# plot the graphs of hits versus number of occurrences
#./job5.R $MIN_YEAR $MAX_YEAR $OUT_DIR
./job5.R $MIN_YEAR $MAX_YEAR $OUT_DIR

# calculate the lowest "large" value
export UPPER_BOUND=`./job6.py $MIN_YEAR $MAX_YEAR 100 $OUT_DIR`

echo "upper bound = " $UPPER_BOUND

# for each year, get the number of calls that appear 1, 2, 3, ... UPPER_BOUND times
./job4.sh $UPPER_BOUND

#./job5.py $MIN_YEAR $MAX_YEAR $UPPER_BOUND $OUT_DIR

export LOWER_BOUND=`expr $UPPER_BOUND + 1`

echo "lower bound = " $LOWER_BOUND

# for each year from MIN_YEAR to MAX_YEAR, get the number of calls that
# appear LOWER_BOUND or more times times
./job7.sh

# create the final plot of CQ activity
./job8.R $MIN_YEAR $MAX_YEAR $UPPER_BOUND $OUT_DIR
