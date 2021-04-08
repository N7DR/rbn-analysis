#! /bin/bash 

# Create sorted files of all the posted calls (including dupes), per year and per band
# This runs jobs in parallel

# extract the CW data for a specific band and year, and write to a file
# $1 = YEAR
# $2 = BAND
filter_rbn_data() 
{ rbncat $1 | awk 'BEGIN{FS=","}; $13=="" {print $0}; $13=="CW" {print $0}' | grep ",$2""m," | awk 'BEGIN{FS=","}; {print $6};' | sort > $OUT_DIR/$1.CW.$2.dx.srt
}
export -f filter_rbn_data

for YEAR in $(seq $MIN_YEAR $MAX_YEAR)
do
  for BAND in 160 80 40 30 20 17 15 12 10
  do
    sem --id $$ $N_JOBS filter_rbn_data $YEAR $BAND
  done
done

sem --id $$ --wait

# create the annual "HF" files, which include all the usual HF bands
for YEAR in $(seq $MIN_YEAR $MAX_YEAR)
do
  if [ -s "$OUT_DIR/$YEAR.CW.HF.dx.srt" ]; then
    rm "$OUT_DIR/$YEAR.CW.HF.dx.srt"
  fi
  
  for BAND in 160 80 40 30 20 17 15 12 10
  do
    cat $OUT_DIR/$YEAR.CW.$BAND.dx.srt >> $OUT_DIR/$YEAR.CW.HF.dx.srt
  done
  
  sort -o $OUT_DIR/$YEAR.CW.HF.dx.srt $OUT_DIR/$YEAR.CW.HF.dx.srt
done
