#!/bin/bash

########################################################################
#                                                                      #
# EXOD - EPIC-pn XMM-Newton Outburst Detector                          #
#                                                                      #
# Full analysis for one observation                                    #
#                                                                      #
# Inés Pastor Marazuela (2019) - ines.pastor.marazuela@gmail.com       #
#                                                                      #
########################################################################

########################################################################
#                                                                      #
# Parsing arguments                                                    #
#                                                                      #
########################################################################

# Default variables
CPUS=12
# Default folders
DIR=/mnt/data/Florent/data
RESULTS=/mnt/data/Florent/results
SCRIPTS=/home/florent/EXOD/scripts
INST=PN

# Input variables
while [[ $# -gt 0 ]]; do
case "$1" in
  # Observation
  -o|-obs|--observation)  OBS=$2
  shift; shift ;;
  # Variables
  -cpus|--cpus)           CPUS=${2:-$CPUS}
  shift; shift ;;
  -i|--inst)              INST=${2:-$INST}
  shift; shift ;;
  # Folders
  -d|-dir|--directory)    DIR=${2:-$DIR}
  shift; shift ;;
  -s|--scripts)           SCRIPTS=${2:-$SCRIPTS}
  shift; shift ;;
  # Forcing analysis 
  -f|--force)             F=${2:-false}
  shift; shift ;;
esac
done

echo -e "\n"
echo -e "\tOBSERVATION = ${OBS}"
echo -e "\tDIRECTORY   = ${DIR}"
echo -e "\tSCRIPTS     = ${SCRIPTS}\n"

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
#
#if [ -f $DIR/$obs/*IEVLI.FTZ -a -f $DIR/$obs/*FBKTSR*.FTZ -a -f $DIR/$obs/*SUM.ASC ] && [ $F = false ]; then
#  echo "Files downloaded. Skipping"
#else
#
#  Title "DOWNLOADING FILES"
#  bash $SCRIPTS/download_observation.sh $DIR $OBS $INST
#
#fi

cd $DIR/$obs

# Filtering events

#if [ -f ${INST}_clean.fits -a -f ${INST}_gti.fits -a -f ${INST}_image.fits ] && [ $F = false ]; then
#  echo "Files filtered. Skipping"
#else
#
#  Title "FILTERING EVENTS"
#  bash $SCRIPTS/filtering.sh -f $DIR -o $OBS -s $SCRIPTS -i $INST
#
#fi

# Applying detector

Title "APPLYING DETECTOR"

if [ -f $(var CLEAN_FILE) -a -f $(var GTI_FILE) -a -f $(var IMG_FILE) ] && [ $F = false ]; then
  echo "Variability computed. Rendering"
  nv="--novar"
else nv=""; fi

  # 8 100 3 1.0
  python3 -W"ignore" $SCRIPTS/detector.py -path $DIR/$OBS -out $RESULTS/$OBS -bs 3 -dl 8 -tw 100 -gtr 1.0 -mta $CPUS -inst $INST --render $nv
  # 6 30 3 1.0
  python3 -W"ignore" $SCRIPTS/detector.py -path $DIR/$OBS -out $RESULTS/$OBS -bs 3 -dl 6 -tw 30 -gtr 1.0 -mta $CPUS -inst $INST --render $nv
  # 4 10 3 1.0 
  python3 -W"ignore" $SCRIPTS/detector.py -path $DIR/$OBS -out $RESULTS/$OBS -bs 3 -dl 4 -tw 10 -gtr 1.0 -mta $CPUS -inst $INST --render $nv
  # 3 3 3 1.0
  python3 -W"ignore" $SCRIPTS/detector.py -path $DIR/$OBS -out $RESULTS/$OBS -bs 3 -dl 3 -tw 3 -gtr 1.0 -mta $CPUS -inst $INST --render $nv

# Rendering all

Title "RENDERING"

python3 -W"ignore" $SCRIPTS/render_all.py -path $RESULTS/$OBS -inst $INST

