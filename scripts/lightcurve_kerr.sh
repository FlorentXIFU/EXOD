#!/bin/bash

################################################################################
#                                                                              #
# EXOD-v2 - EPIC XMM-Newton Outburst Detector                                  #
#                                                                              #
# Proceed lightcurves on all sources found (with max=5 !)                      #
#                                                                              #
# Florent Castellani  (2020) -  castellani.flo@gmail.com                       #
#                                                                              #
################################################################################


FOLDER=/mnt/data/Florent/data
SCRIPTS=/home/florent/EXOD/scripts
input_log=/home/florent/results.log
output_log=/home/florent/lightcurve_results.log

while read line ; do

# Extracting observation number
OBS=$(echo $line | awk '{print $1}')

# Extracting number of detected sources
nbPN=$(echo $line | grep 'PN=' | sed "s/.*PN=//" | awk '{print $1}')
nbM1=$(echo $line | grep 'M1=' | sed "s/.*M1=//" | awk '{print $1}')
nbM2=$(echo $line | grep 'M2=' | sed "s/.*M2=//" | awk '{print $1}')

# Changing to zero if no source
nbPN=$((nbPN+0))
nbM1=$((nbM1+0))
nbM2=$((nbM2+0))

# Extracting lightcurves (max 5) for each instrument
countPN=1
while [[ $countPN -le $nbPN ]] && [[ $countPN -le 5 ]] ; do
  bash $SCRIPTS/lightcurve.sh $FOLDER/$OBS $SCRIPTS PN $countPN 8 100 1.0 5 $output_log
  ((++countPN))
done

echo -e "Lighcurves done for $OBS with PN instrument"

countM1=1
while [[ $countM1 -le $nbM1 ]] && [[ $countM1 -le 5 ]] ; do
  bash $SCRIPTS/lightcurve.sh $FOLDER/$OBS $SCRIPTS M1 $countM1 8 100 1.0 5 $output_log
  ((++countM1))
done

echo -e "Lighcurves done for $OBS with M1 instrument"

countM2=1
while [[ $countM2 -le $nbM2 ]] && [[ $countM2 -le 5 ]] ; do
  bash $SCRIPTS/lightcurve.sh $FOLDER/$OBS $SCRIPTS M2 $countM2 8 100 1.0 5 $output_log
  ((++countM2))
done

echo -e "Lighcurves done for $OBS with M2 instrument"

done < $input_log


