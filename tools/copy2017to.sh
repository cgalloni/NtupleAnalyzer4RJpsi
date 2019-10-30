#! /bin/bash

CHANNELS='mutau eletau mumu tautau'
YEAR="2018"
TAG=""
while getopts "c:t:y:" option; do case "${option}" in
  c) CHANNELS="${OPTARG}";;
  t) TAG="${OPTARG}";;
  y) YEAR="${OPTARG}";;
esac done

[ "$YEAR" != 2016 -a "$YEAR" != 2018 ] && echo ">>> ERROR! Year $YEAR not valid!" && exit 1

SCRATCHOLD="/scratch/ineuteli/analysis/LQ_2017"
SCRATCHNEW="/scratch/ineuteli/analysis/LQ_$YEAR"

if [ "$YEAR" == "2016" ]; then
  SAMPLES="
    DY/DY4JetsToLL_M-50
  "
else
  SAMPLES="
    WJ/WJetsToLNu
  "
fi

for channel in $CHANNELS; do
  [[ $channel = '#'* ]] && continue
  for samplename in $SAMPLES; do
    [[ $samplename = '#'* ]] && continue
    echo $samplename
    
    fileold="$SCRATCHOLD/${samplename}_${channel}${TAG}.root"
    filenew="$SCRATCHNEW/${samplename}_${channel}${TAG}.root"  
    [ ! -e $fileold ] && echo "Warning! $fileold does not exist!" && continue 
    
    echo "Copying $fileold to $filenew!"
    cp -v $fileold $filenew
  done
done
