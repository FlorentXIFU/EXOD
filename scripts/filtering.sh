#!/bin/bash

########################################################################
#                                                                      #
# EXOD - EPIC-pn XMM-Newton Outburst Detector                          #
#                                                                      #
# Events file filtering                                                #
#                                                                      #
# Inés Pastor Marazuela (2019) - ines.pastor.marazuela@gmail.com       #
#                                                                      #
########################################################################

###
# Parsing arguments                                                            
###

# Default variables
RATE=0.5	# according to SAS documentation (PN Rate = 0.4 and MOS Rate = 0.35)
FOLDER=/home/monrillo/data
SCRIPTS=/home/monrillo/EXOD/scripts
INST=PN

# Input variables
while [[ $# -gt 0 ]]; do
case "$1" in
  -o|-obs|--observation) OBS=${2}
  shift; shift ;;
  -r|--rate)             RATE=${2:-$RATE}
  shift; shift ;;
  -i|--instrument)       INST=${2:-$INST}
  shift; shift ;;
  -f|--folder)           FOLDER=${2:-$FOLDER}
  shift; shift ;;
  -s|--scripts)          SCRIPTS=${2:-$SCRIPTS}
  shift; shift ;;
esac
done

echo -e "\tFOLDER      = ${FOLDER}"
echo -e "\tOBSERVATION = ${OBS}"
echo -e "\tINSTRUMENT  = ${INST}"
echo -e "\tRATE        = ${RATE}"


path=$FOLDER/$OBS

###
# Defining functions
###

Title(){
  message=$1; i=0; x='===='
  while [[ i -lt ${#message} ]]; do x='='$x; ((++i)); done
  echo -e "\n\t  $message \n\t$x"
}

title(){
  message=$1; i=0; x=----
  while [[ i -lt ${#message} ]]; do x=-$x; ((++i)); done
  echo -e "\n\t  $message \n\t$x"
}

# Useful
########################################################################

var(){
  x=$1
  out=$(cat $SCRIPTS/file_names.py | grep ^$x | awk '{print $3}' | sed 's/"//g')
  echo $out
}

########################################################################
#                                                                      #
# Main programme                                                       #
#                                                                      #
########################################################################

Title "Filtering observation $OBS"

###
# Preliminaries
###

title "Preliminaries"

# Setting up SAS
cd $path
export SAS_ODF=$path
export SAS_CCF=$path/ccf.cif
export HEADAS=$(var HEADAS)
. $HEADAS/headas-init.sh
. $(var SAS)

if [ ! -f $path/ccf.cif ]; then cifbuild; fi

###
# Filtering
###

title "Cleaning events file"

# File names
if [ "$INST" == "PN" ]; then
  org_file=$(ls $path/*${OBS}PN*PIEVLI*)
  clean_file=$path/PN_clean.fits
  gti_file=$path/PN_gti.fits
  img_file=$path/PN_image.fits
  rate_file=$path/PN_rate.fits
  l=P

elif [ "$INST" == "M1" ]; then
  org_file=$(ls $path/*${OBS}M1*MIEVLI*)
  clean_file=$path/M1_clean.fits
  gti_file=$path/M1_gti.fits
  img_file=$path/M1_image.fits
  rate_file=$path/M1_rate.fits
  l=M

elif [ "$INST" == "M2" ]; then
  org_file=$(ls $path/*${OBS}M2*MIEVLI*)
  clean_file=$path/M2_clean.fits
  gti_file=$path/M2_gti.fits
  img_file=$path/M2_image.fits
  rate_file=$path/M2_rate.fits
  l=M

else
  echo "ERROR: Instrument not recognized"
  exit
fi

echo -e "\tRAW FILE   = ${org_file}"
echo -e "\tCLEAN FILE = ${clean_file}"
echo -e "\tGTI FILE   = ${gti_file}"
echo -e "\tIMAGE FILE = ${img_file}"
echo -e "\tRATE FILE  = ${rate_file}"

# Creating GTI
title "Creating GTI"

if [ "$INST" == "PN" ]; then

  evselect table=$org_file withrateset=Y rateset=$rate_file maketimecolumn=Y timebinsize=100 makeratecolumn=Y expression='#XMMEA_EP && (PI in [10000:12000]) && (PATTERN==0)' -V 0

elif [ "$INST" == "M1" ] || [ "$INST" == "M2" ]; then

  evselect table=$org_file withrateset=Y rateset=$rate_file maketimecolumn=Y timebinsize=100 makeratecolumn=Y expression='#XMMEA_EM && (PI>10000) && (PATTERN==0)' -V 0

fi

if [[ $RATE != [0-9]* ]]; then
    echo "Opening PN_rate.fits" 
    fv $rate_file &
    read -p "Choose the GTI cut rate : " RATE
fi
echo "Creating Good Time Intervals with threshold RATE=$RATE"

tabgtigen table=$rate_file expression="RATE<=$RATE" gtiset=$gti_file -V 0

# Cleaning events file

if [ "$INST" == "PN" ]; then

  evselect table=$org_file withfilteredset=Y filteredset=$clean_file destruct=Y keepfilteroutput=T expression="#XMMEA_EP && gti($gti_file,TIME) && (PATTERN<=4) && (PI in [500:12000])" -V 0

elif [ "$INST" == "M1" ] || [ "$INST" == "M2" ]; then

  evselect table=$org_file withfilteredset=Y filteredset=$clean_file destruct=Y keepfilteroutput=T expression="#XMMEA_EM && gti($gti_file,TIME) && (PATTERN<=12) && (PI in [200:10000])" -V 0
# PI > 500 for avoiding thermal noise ?

fi

#ds9 $events_file -bin factor 64 -scale log -cmap bb -mode region &

# Creating image file

evselect table=$clean_file imagebinning=binSize imageset=$img_file withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=80 yimagebinsize=80 -V 0


if [ "$INST" == "PN" ]; then 
  echo > $path/PN_processing.log "Rate: $RATE"

elif [ "$INST" == "M1" ]; then 
  echo > $path/M1_processing.log "Rate: $RATE"

elif [ "$INST" == "M2" ]; then 
  echo > $path/M2_processing.log "Rate: $RATE"

fi

echo "Rate = ..." >> $path/${INST}_processing.log

echo "The end" 
date 
