#! /bin/bash
 
# for each year from MIN_YEAR to MAX_YEAR, get the number of calls that
# appear LOWER_BOUND or more times times

# extract the appearance data for >= LOWER_BOUND appearances for each year for a specific band, and write to a file
# $1 = BAND
filter_n_ge_appearances() 
{ for appearances in $(seq $LOWER_BOUND $LOWER_BOUND)
  do
    for YEAR in $(seq $MIN_YEAR $MAX_YEAR)
    do
      echo -n `awk -v ap="$appearances" '++a[$1]==ap{ print $1 }' $OUT_DIR/$YEAR.CW.$1.dx.srt | wc -l` >> $OUT_DIR/ge$LOWER_BOUND.$1
      if [ $YEAR -ne $MAX_YEAR ];
      then
        echo -n , >> $OUT_DIR/ge$LOWER_BOUND.$1
      fi
    done
    echo >> $OUT_DIR/ge$LOWER_BOUND.$1
  done
}
export -f filter_n_ge_appearances

for BAND in HF 160 80 40 30 20 17 15 12 10
do
  if [ -s "$OUT_DIR/ge$LOWER_BOUND.$BAND" ]
  then
    rm $OUT_DIR/ge$LOWER_BOUND.$BAND
  fi
  
  sem --id $$ $N_JOBS filter_n_ge_appearances $BAND
done

sem --id $$ --wait
