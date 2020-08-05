#!/bin/bash

################################################################################
#                                                                              #
# EXOD-v2 - EPIC XMM-Newton Outburst Detector                                  #
#                                                                              #
# Check if a variability source has been found                                 #
#                                                                              #
# Florent Castellani  (2020) -  castellani.flo@gmail.com                       #
#                                                                              #
################################################################################


FOLDER=/mnt/data/Florent/results
output_log=/home/florent/output.log

while read line; do

# Initialise
inst=''
testPN=''
testM1=''
testM2=''

# Testing if the variability has been done for each EPIC instrument
if [ -f $FOLDER/$line/8_100_5_1.0_PN/ds9_variable_sources.reg ] ; then
    testPN=$(cat $FOLDER/$line/8_100_5_1.0_PN/ds9_variable_sources.reg | grep 'text="'1'"' | awk '{print $1}')
else
    inst="$inst  PN(Prob!!!)"
fi

if [ -f $FOLDER/$line/8_100_5_1.0_M1/ds9_variable_sources.reg ] ; then
    testM1=$(cat $FOLDER/$line/8_100_5_1.0_M1/ds9_variable_sources.reg | grep 'text="'1'"' | awk '{print $1}')
else
    inst="$inst  M1(Prob!!!)"
fi

if [ -f $FOLDER/$line/8_100_5_1.0_M2/ds9_variable_sources.reg ] ; then
    testM2=$(cat $FOLDER/$line/8_100_5_1.0_M2/ds9_variable_sources.reg | grep 'text="'1'"' | awk '{print $1}')
else
    inst="$inst  M2(Prob!!!)"
fi

# Testing if at least one variable source has been found for each EPIC instrument
if [[ "$testPN" == 'circle' ]]; then inst="$inst  PN"; fi
if [[ "$testM1" == 'circle' ]]; then inst="$inst  M1"; fi
if [[ "$testM2" == 'circle' ]]; then inst="$inst  M2"; fi

# Results are written in a log file
echo -e >> $output_log "$line $inst"

done < /home/florent/EXOD/essai.txt

