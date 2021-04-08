#! /bin/bash

# for each year, get the number of calls that appear 1, 2, 3, ... UPPER_BOUND times

export UPPER_BOUND=$1

# extract the appearance data for 1 to UPPER_BOUND appearances for each year for a specific band, and write to a file
# $1 = BAND
filter_n_exact_appearances() 
{ for appearances in $(seq 1 $UPPER_BOUND)
  do
    for YEAR in $(seq $MIN_YEAR $MAX_YEAR)
    do
      echo -n `awk -v ap="$appearances" '{++a[$1]}END{ for(i in a) if(a[i]==ap) print i }' $OUT_DIR/$YEAR.CW.$1.dx.srt | wc -l` >> $OUT_DIR/exact_appearances_1_$UPPER_BOUND.$1
      if [ $YEAR -ne $MAX_YEAR ];
      then
        echo -n , >> $OUT_DIR/exact_appearances_1_$UPPER_BOUND.$1
      fi
    done
    echo >> $OUT_DIR/exact_appearances_1_$UPPER_BOUND.$1
  done
}
export -f filter_n_exact_appearances

for BAND in HF 160 80 40 30 20 17 15 12 10
do
  if [ -s "$OUT_DIR/exact_appearances_1_$UPPER_BOUND.$BAND" ]
  then
    rm $OUT_DIR/exact_appearances_1_$UPPER_BOUND.$BAND
  fi
  
  sem --id $$ $N_JOBS filter_n_exact_appearances $BAND
done

sem --id $$ --wait

# each output line is the number of calls for the nth appearance number for each year from MIN_YEAR to MAX_YEAR,
# where n is the line number
 
