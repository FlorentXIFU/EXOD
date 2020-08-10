#!/bin/bash

########################################################################
#                                                                      #
# EXODUS - EPIC XMM-Newton Outburst Detector Ultimate System           #
#                                                                      #
# Full analysis for one observation with the 3 EPICs (PN and MOS)      #
#                                                                      #
# Florent Castellani (2020) - castellani.flo@gmail.com                 #
#                                                                      #
########################################################################

########################################################################
#                                                                      #
# Parsing arguments                                                    #
#                                                                      #
########################################################################

# Default variables
DL=8 ; TW=100 ; GTR=1.0 ; BS=3 ; CPUS=8
# Default folders
DIR=/home/monrillo/data
SCRIPTS=/home/monrillo/EXOD/scripts
F=false

# Input variables
while [[ $# -gt 0 ]]; do
case "$1" in
  # Observation
  -o|-obs|--observation)  OBS=$2
  shift; shift ;;
  # Variables
  -dl|--detection-level)  DL=${2:-$DL}
  shift; shift ;;
  -tw|--time-window)      TW=${2:-$TW}
  shift; shift ;;
  -gtr|--good-time-ratio) GTR=${2:-$GTR}
  shift; shift ;;
  -bs|--box-size)         BS=${2:-$BS}
  shift; shift ;;
  -cpus|--cpus)           CPUS=${2:-$CPUS}
  shift; shift ;;
  # Folders
  -d|-dir|--directory)    DIR=${2:-$DIR}
  shift; shift ;;
  -s|--scripts)           SCRIPTS=${2:-$SCRIPTS}
  shift; shift ;;
  # Forcing analysis 
  -f|--force)             F=${2:-$F}
esac
done

echo -e "\n"
echo -e "\tOBSERVATION = ${OBS}"
echo -e "\tDIRECTORY   = ${DIR}"
echo -e "\tSCRIPTS     = ${SCRIPTS}"
echo -e "\tFORCED      = ${F}\n"

########################################################################
#                                                                      #
# Defining functions                                                   #
#                                                                      #
########################################################################

Title(){
  message=$1; i=0; x='===='
  while [[ i -lt ${#message} ]]; do x='='$x; ((++i)); done
  echo -e "\n\t  $message \n\t$x"
}

title(){
  message=$1; i=0; x='----'
  while [[ i -lt ${#message} ]]; do x='-'$x; ((++i)); done
  echo -e "\n\t  $message \n\t$x"
}

# Useful
########################################################################

var(){
  x=$1
  out=$(cat $SCRIPTS/file_names.py | grep ^$x | awk '{print $3}' | sed 's/"//g')
  echo $out
}

waitForFinish()
{
  STRING=$1;
  # wait until jobs have started
  sleep 1
  # check, twice, whether all done
  for i in 1 2 ; do
    job=99
    while [ $job -gt 0 ] ; do sleep 10; job=`top -b | head -n 40 | grep ${STRING} | wc -l`; done
  done
}

########################################################################
#                                                                      #
# Main programme                                                       #
#                                                                      #
########################################################################

# Downloading files

for inst in 'PN' 'M1' 'M2' ; do
  if [ -f $DIR/$OBS/*${OBS}${inst}*IEVLI*.FTZ -a -f $DIR/$OBS/*${OBS}${inst}*FBKTSR*.FTZ ] && [[ "$F" = false ]]; then
    echo "Files downloaded for $inst. Skipping"
  else
    Title "DOWNLOADING FILES"
    bash $SCRIPTS/download_observation.sh $DIR $OBS $inst
  fi
done

cd $DIR/$OBS

# Filtering events

for inst in 'PN' 'M1' 'M2' ; do
  if [ -f ${inst}_clean.fits -a -f ${inst}_gti.fits -a -f ${inst}_image.fits ] && [ "$F" = false ]; then
    echo "Files filtered for $inst. Skipping"
  else
    Title "FILTERING EVENTS"
    bash $SCRIPTS/filtering.sh -f $DIR -o $OBS -s $SCRIPTS -i $inst
  fi
done

# Applying detector

Title "APPLYING DETECTOR"

  # PN
  python3 -W"ignore" $SCRIPTS/detector.py -path $DIR/$OBS -bs $BS -dl $DL -tw $TW -gtr $GTR -mta $CPUS -inst PN --render --novar
  # MOS 1
  python3 -W"ignore" $SCRIPTS/detector.py -path $DIR/$OBS -bs $BS -dl $DL -tw $TW -gtr $GTR -mta $CPUS -inst M1 --render --novar
  # MOS 2 
  python3 -W"ignore" $SCRIPTS/detector.py -path $DIR/$OBS -bs $BS -dl $DL -tw $TW -gtr $GTR -mta $CPUS -inst M2 --render --novar

# Rendering exodus

Title "RENDERING"

python3 -W"ignore" $SCRIPTS/render_exodus.py -path $DIR/$OBS -bs $BS -dl $DL -tw $TW -gtr $GTR

# Lightcurves in case of triple correlations

if [ ! -f $DIR/$OBS/triple_correlation.txt ] ; then	# Exiting if no triple correlation
    exit
fi

Title "LIGHTCURVES"

while read line; do

idPN=$(echo $line | awk '{print $1}')
idM1=$(echo $line | awk '{print $3}')
idM2=$(echo $line | awk '{print $5}')
inter=$DIR/$OBS/inter_triple_PN_${idPN}_M1_${idM1}_M2_${idM2}_lc.txt

# Checking whether already done or not
if [ ! -f $inter ] ; then
  # PN
  bash $SCRIPTS/lightcurve.sh $DIR/$OBS $SCRIPTS PN $idPN $DL $TW $GTR $BS $inter
  # MOS 1
  bash $SCRIPTS/lightcurve.sh $DIR/$OBS $SCRIPTS M1 $idM1 $DL $TW $GTR $BS $inter
  # MOS 2 
  bash $SCRIPTS/lightcurve.sh $DIR/$OBS $SCRIPTS M2 $idM2 $DL $TW $GTR $BS $inter
fi

# Rendering for triple correlation lightcurves

python3 -W"ignore" $SCRIPTS/lcurve_exodus.py -path $DIR -obs $OBS -file $inter -tw $TW -ipn $idPN -im1 $idM1 -im2 $idM2

done < $DIR/$OBS/triple_correlation.txt






