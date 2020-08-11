#!/bin/bash

########################################################################
#                                                                      #
# EXOD-v2 - EPIC all instruments XMM-Newton Outburst Detector          #
#                                                                      #
# Events file filtering for Kerr                                       #
#                                                                      #
# Inés Pastor Marazuela (2019) - ines.pastor.marazuela@gmail.com       #
# Florent Castellani    (2020) - castellani.flo@gmail.com              #
#                                                                      #
########################################################################

###
# Parsing arguments                                                            
###

# Default variables
RATE=0
FOLDER=/mnt/data/Florent/data
#FOLDER_EVTS=/mnt/xmmcat/4xmm_products
FOLDER_EVTS=/mnt/xmmcat/4XMM_data/DR10_incr_data
SCRIPTS=/home/florent/EXOD/scripts
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


path_evts=$FOLDER_EVTS/$OBS/product
path_odf=$FOLDER_EVTS/$OBS/odf
path_out=$FOLDER/$OBS

echo -e "\tFOLDER_OUT 	= ${path_out}"
echo -e "\tFOLDER_EVTS 	= ${path_evts}"
echo -e "\tFOLDER_ODF 	= ${path_odf}"
echo -e "\tOBSERVATION 	= ${OBS}"
echo -e "\tINSTRUMENT  	= ${INST}"


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

if [ ! -d $path_out ]; then mkdir $path_out; fi

cd $path_out

export SAS_ODF=$path_odf
export SAS_CCF=$path_out/ccf.cif
export HEADAS=$(var HEADAS)
. $HEADAS/headas-init.sh
. $(var SAS)

if [ ! -f $path_out/ccf.cif ]; then cifbuild; fi

###
# Filtering
###

title "Cleaning events file"

# File names

org_file=$(ls $path_evts/*${OBS}${INST}*IEVLI*)
clean_file=$path_out/${INST}_clean.fits
gti_file=$path_out/${INST}_gti.fits
img_file=$path_out/${INST}_image.fits
rate_file=$path_out/${INST}_rate.fits


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

if [ $RATE == 0 ]; then
    if [ $INST == PN ] ; then
      RATE=0.5
    else RATE=0.4
    fi
fi


echo "Creating Good Time Intervals with threshold RATE=$RATE"

tabgtigen table=$rate_file expression="RATE<=$RATE" gtiset=$gti_file -V 0

# Cleaning events file

if [ "$INST" == "PN" ]; then

  evselect table=$org_file withfilteredset=Y filteredset=$clean_file destruct=Y keepfilteroutput=T expression="#XMMEA_EP && gti($gti_file,TIME) && (PATTERN<=4) && (PI in [500:12000])" -V 0

elif [ "$INST" == "M1" ] || [ "$INST" == "M2" ]; then

  evselect table=$org_file withfilteredset=Y filteredset=$clean_file destruct=Y keepfilteroutput=T expression="#XMMEA_EM && gti($gti_file,TIME) && (PATTERN<=12) && (PI in [500:10000])" -V 0

fi

# Creating image file

evselect table=$clean_file imagebinning=binSize imageset=$img_file withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=80 yimagebinsize=80 -V 0


echo "Rate = $RATE" >> $path_out/${INST}_processing.log

echo "The end" 
date 
