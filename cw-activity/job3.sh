#! /bin/bash
 
# this is fast enough not to need to be run in parallel

# get the total number of different calls posted for each year and band

for BAND in 160 80 40 30 20 17 15 12 10 HF
do
  if [ -s $OUT_DIR/ncalls.$BAND ]
  then
    rm $OUT_DIR/ncalls.$BAND
  fi

  for YEAR in $(seq $MIN_YEAR $MAX_YEAR)
  do
    echo `uniq $OUT_DIR/$YEAR.CW.$BAND.dx.srt | wc -l` >> $OUT_DIR/ncalls.$BAND
  done
done
