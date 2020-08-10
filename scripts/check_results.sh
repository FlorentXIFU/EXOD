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

cd $FOLDER
observations=(0*)
nb_img=${#observations[@]}
echo $nb_img

for obs in ${observations[@]}; do

# Initialise
inst=''
testPN=''
testM1=''
testM2=''
triple=''

# Testing if the variability has been done for each EPIC instrument
if [ -f $FOLDER/$obs/8_100_5_1.0_PN/ds9_variable_sources.reg ] ; then
    testPN=$(cat $FOLDER/$obs/8_100_5_1.0_PN/ds9_variable_sources.reg | grep 'text="'1'"' | awk '{print $1}')
else
    inst="$inst\tPN(Pb!)"
fi

if [ -f $FOLDER/$obs/8_100_5_1.0_M1/ds9_variable_sources.reg ] ; then
    testM1=$(cat $FOLDER/$obs/8_100_5_1.0_M1/ds9_variable_sources.reg | grep 'text="'1'"' | awk '{print $1}')
else
    inst="$inst\tM1(Pb!)"
fi

if [ -f $FOLDER/$obs/8_100_5_1.0_M2/ds9_variable_sources.reg ] ; then
    testM2=$(cat $FOLDER/$obs/8_100_5_1.0_M2/ds9_variable_sources.reg | grep 'text="'1'"' | awk '{print $1}')
else
    inst="$inst\tM2(Pb!)"
fi

# Testing if at least one variable source has been found for each EPIC instrument
if [[ "$testPN" == 'circle' ]]; then
numPN=$(cat $FOLDER/$obs/8_100_5_1.0_PN/ds9_variable_sources.reg | grep 'text=' | awk '{print $1}' | wc -l)
inst="$inst\tPN=${numPN}"
fi
if [[ "$testM1" == 'circle' ]]; then
numM1=$(cat $FOLDER/$obs/8_100_5_1.0_M1/ds9_variable_sources.reg | grep 'text=' | awk '{print $1}' | wc -l)
inst="$inst\tM1=${numM1}"
fi
if [[ "$testM2" == 'circle' ]]; then
numM2=$(cat $FOLDER/$obs/8_100_5_1.0_M2/ds9_variable_sources.reg | grep 'text=' | awk '{print $1}' | wc -l)
inst="$inst\tM2=${numM2}"
fi

# Testing if triple correlation variability files and lightcurves
if [ -f $FOLDER/$obs/variability_8_100_5_1.0_all_inst.pdf ] ; then
triple="$triple\tvar_all_inst"
fi
if [ -f $FOLDER/$obs/triple*.pdf ] ; then
triple="$triple\ttriple_lc"
fi

# Printing results
echo -e "$obs $inst $triple"

# Results are written in a log file
echo -e >> $output_log "$obs $inst $triple"

done 
