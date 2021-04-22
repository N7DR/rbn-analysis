#! /bin/sh

# Plot a CW activity/popularity metric as a function of time

export MIN_YEAR=2009
export MAX_YEAR=2020

export OUT_DIR='/tmp/cwa-n'

export N_VALUES=12

# ------------------------------------  nothing below this line should need to be changed  ---------------------

if [ $MAX_YEAR -lt $MIN_YEAR ];
then
  echo "MAX_YEAR < MIN_YEAR"
  exit
fi

mkdir -p $OUT_DIR

# extract CW data for bands and years from the RBN dataset and perform initial analysis
export UPPER_BOUND=`./job1.py $MIN_YEAR $MAX_YEAR $OUT_DIR 100 $N_VALUES`

# purely informative output
echo "upper bound = " $UPPER_BOUND

# plot the graphs of hits versus number of occurrences (just to make sure that things look reasonable)
./job2.R $MIN_YEAR $MAX_YEAR $OUT_DIR $N_VALUES

# create the final metric-$N_VALUES.png plot of CQ activity
./job3.R $MIN_YEAR $MAX_YEAR $UPPER_BOUND $OUT_DIR $N_VALUES
