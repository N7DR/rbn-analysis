#! /bin/bash

# this is fast enough not to need to be run in parallel

# get the total number of posts for each year and band

for BAND in 160 80 40 30 20 17 15 12 10 HF
do
  if [ -s $OUT_DIR/nposts.$BAND ]
  then
    rm $OUT_DIR/nposts.$BAND
  fi
  
  for YEAR in $(seq $MIN_YEAR $MAX_YEAR)
  do
    echo `wc -l $OUT_DIR/$YEAR.CW.$BAND.dx.srt | cut -d " " -f 1` >> $OUT_DIR/nposts.$BAND
  done
done 
