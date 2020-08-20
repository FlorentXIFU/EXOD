#!/bin/bash

################################################################################
#                                                                              #
# EXOD-v2 - EPIC XMM-Newton Outburst Detector                                  #
#                                                                              #
# Manual lightcurve generation of the detected variable sources                #
#                                                                              #
# Florent Castellani  (2020) -  castellani.flo@gmail.com                       #
#                                                                              #
################################################################################

################################################################################
#                                                                              #
# Parsing arguments                                                            #
#                                                                              #
################################################################################

# Default variables
DL=24 ; TW=100 ; GTR=1.0 ; BS=5; INST=PN; ID=1
# Default folders
FOLDER=/mnt/data/Florent/data
SCRIPTS=/home/florent/EXOD/scripts

# Input variables
while [[ $# -gt 0 ]]; do
case "$1" in
  -o|-obs|--observation)  OBS=${2}
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
  -i|--inst)              INST=${2:-$INST}
  shift; shift ;;
  -id|--source-id)        ID=${2:-$ID}
  shift; shift ;;
  # Folders
  -f|--folder)            FOLDER=${2:-$FOLDER}
  shift; shift ;;
  -s|--scripts)           SCRIPTS=${2:-$SCRIPTS}
  shift; shift ;;
esac
done

output_log=/mnt/data/Florent/results/$OBS/excluded_manual/output.log
path=$FOLDER/$OBS

###
# Defining functions
###

title1(){
  message=$1; i=0; x='===='
  while [[ i -lt ${#message} ]]; do x='='$x; ((++i)); done
  echo -e "\n\t  $message \n\t$x\n"
}

title2(){
  message="$1 $OBS"; i=0; x='----'
  while [[ i -lt ${#message} ]]; do x='-'$x; ((++i)); done
  echo -e "\n\t  $message \n\t$x"
}

title3(){
  message="$1 $OBS"; echo -e "\n # $message"
}

input(){
  message="$1"; var="$2"
  read -p "$(tput setaf 6)$message $(tput sgr 0)" out 
  printf -v $var $out
}

################################################################################

start=`date +%s`

title1 "Lightcurve Obs. $OBS Src. $ID"

echo -e "\tFOLDER          = ${FOLDER}"
echo -e "\tSCRIPTS         = ${SCRIPTS}"
echo -e "\tOUTPUT LOG      = ${output_log}\n"
echo -e "\tDETECTION LEVEL = ${DL}"
echo -e "\tTIME WINDOW     = ${TW}"
echo -e "\tGOOD TIME RATIO = ${GTR}" 
echo -e "\tBOX SIZE        = ${BS}"
echo -e "\tINSTRUMENT      = ${INST}"

# Selecting the files and paths
fbks=/mnt/data/Florent/fbktsr/${OBS}
clean_file=$path/${inst}_clean.fits
gti_file=$path/${inst}_gti.fits
img_file=$path/${inst}_image.fits
nosrc_file=$path/${inst}_sourceless.fits

results=/mnt/data/Florent/results/${OBS}
path_out=/mnt/data/Florent/results/${OBS}/lcurve_${TW}_${inst}

fbk_file=$(ls $fbks/*$OBS*$INST*FBKTSR*)

if [ ! -d $path_out ]; then mkdir $path_out; fi
cd $path_out

# Setting SAS tools
export SAS_ODF=$path
export SAS_CCF=$path/ccf.cif
export HEADAS=/usr/local/heasoft-6.22.1/x86_64-unknown-linux-gnu-libc2.19/
. $HEADAS/headas-init.sh
. /usr/local/SAS/xmmsas_20170719_1539/setsas.sh

##################################################################################################################################################################################
# Source selection
echo "  Select the source and background extraction region (X,Y,R): "
if [ ! -f $path/${DL}_${TW}_1.0_${BS}/sources.pdf ]; then python3 /home/pastor/python3 -Wignore $SCRIPTS/renderer.py $folder/$OBS/${DL}_${TW}_1.0_${BS} $clean_file -obs $OBS -tw $TW -dl $DL
fi
if [ $ID == "1" ]; then 
ds9 $clean_file -bin factor 64 -scale log -cmap b -mode region &
evince $path/${DL}_${TW}_1.0_${BS}/sources.pdf &
fi
evselect table=$clean_file imagebinning=binSize imageset=$img_file withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=80 yimagebinsize=80
data=$(cat $path/${DL}_${TW}_1.0_${BS}/detected_variable_sources.csv | grep "^${ID};")
title3 $data

###
# Source name and coordinates
###

IFS=';' read -r -a array <<< "$data"
n=${array[0]}
ccd=${array[1]}
rawx=${array[2]}
rawy=${array[3]}
srcR=$((${array[4]} * 64))

ecoordconv imageset=$img_file coordtype=raw x=$rawx y=$rawy ccdno=$ccd |grep 'X: Y:'

input "Proceed? [y/n] " reply
if [[ $reply = [n,N]* ]] ; then exit; fi

echo -e "\n"
input "Source position     [X] " srcX
input "Source position     [Y] " srcY 
input "Background position [X] " bgdX
input "Background position [Y] " bgdY
input "Radius              [R] " R
echo -e "\n"

srccoord=$(ecoordconv imageset=$img_file coordtype=POS x=$srcX y=$srcY pos2eqpos=yes | tee /dev/tty|grep ' RA: DEC: ' | sed 's/ RA: DEC: //g')

##################################################################################################################################################################################

###
# Source name and coordinates
###

# Right ascension in hours
RA=$(bc <<< "scale=5; $RAd / 15")

if [[ $RA == .* ]]; then RA=0$RA; fi
h=$(echo $RA | sed "s/.[0-9]*$//g")
m=$(bc <<< "scale=5; ($RA - $h) * 60" | sed "s/.[0-9]*$//g")
s=$(bc <<< "scale=2; (($RA - $h) * 60 - $m) * 60" | sed "s/.[0-9]*$//")
if [ ${#h} == 1 ]; then h=0$h ; elif [ ${#h} == 0 ] ; then h=00 ; fi
if [ ${#m} == 1 ]; then m=0$m ; elif [ ${#m} == 0 ] ; then m=00 ; fi
if [ ${#s} == 1 ]; then s=0$s ; elif [ ${#s} == 0 ] ; then s=00; fi

# Declination

# DEC=$(echo $srccoord | awk '{print $2}')
if [[ $DEC == -* ]]; then DEC=${DEC#"-"}; link="-"; else link="_"; fi
if [[ $DEC == .* ]]; then DEC=0$DEC; fi
dg=$(echo $DEC | sed "s/.[0-9]*$//g")
am=$(bc <<< "scale=5; ($DEC - $dg) * 60" | sed "s/.[0-9]*$//g")
as=$(bc <<< "scale=2; (($DEC - $dg) * 60 - $am) * 60" | sed "s/.[0-9]*$//")
if [ ${#dg} == 1 ]; then dg=0$dg ; elif [ ${#dg} == 0 ] ; then dg=00 ; fi
if [ ${#am} == 1 ]; then am=0$am ; elif [ ${#am} == 0 ] ; then am=00 ; fi
if [ ${#as} == 1 ]; then as=0$as ; elif [ ${#as} == 0 ] ; then as=00; fi
if [[ $link == "-" ]]; then DEC=$link$DEC; fi

sleep 1
# Source namedg$am$as
src=J$h$m$s$link$dg$am$as
echo -e "\n\t$src\n"

###
# Background extraction region
###

if [ ! -f $nosrc_file ]; then
evselect table=$clean_file withfilteredset=Y filteredset=$nosrc_file destruct=Y keepfilteroutput=T expression="region($fbk_file:REGION,X,Y)" -V 0
fi

bgdXY=$(ebkgreg withsrclist=no withcoords=yes imageset=$img_file x=$RAd y=$DEC r=$srcRas coordtype=EQPOS | grep 'X,Y Sky Coord.' | head -1 | awk '{print$5$6}')
bgdexp="(X,Y) in CIRCLE($bgdXY,$srcR)"

sleep 1
echo -e "\nExtracting data obs. $observation source $src with the following coordinates: \n  Source     : $srcexp\n  Background : $bgdexp"


################################################################################
#                                                                              #
# Lightcurve generation                                                        #
#                                                                              #
################################################################################

title2 "Extracting lightcurve"
if [ ! -f $path/${inst}_gti.wi ]; then gti2xronwin -i $path/${inst}_gti.fits -o $path/${inst}_gti.wi; fi

title3 "Frame time"
frmtime=$(hexdump -e '80/1 "%_p" "\n"' $clean_file | grep -m 1 FRMTIME | awk '{print $3}')
frmtime=$(bc <<< "$frmtime * 0.001")
frmtime=$(bc <<< "scale=3; ($frmtime + 0.001)/1")
if [[ $frmtime == .* ]]; then frmtime=0$frmtime; fi

sleep 1
echo -e "\nFrame time = $frmtime"

title3 "evselect $frmtime s"
evselect table=$clean_file energycolumn=PI expression="$srcexp" withrateset=yes rateset=$path_out/${src}_lc_${frmtime}_src.lc timebinsize=$frmtime maketimecolumn=yes makeratecolumn=yes -V 0
evselect table=$nosrc_file energycolumn=PI expression="$bgdexp" withrateset=yes rateset=$path_out/${src}_lc_${frmtime}_bgd.lc timebinsize=$frmtime maketimecolumn=yes makeratecolumn=yes -V 0

title3 "evselect $TW s"
evselect table=$clean_file energycolumn=PI expression="$srcexp" withrateset=yes rateset=$path_out/${src}_lc_${TW}_src.lc timebinsize=$TW maketimecolumn=yes makeratecolumn=yes -V 0
evselect table=$nosrc_file energycolumn=PI expression="$bgdexp" withrateset=yes rateset=$path_out/${src}_lc_${TW}_bgd.lc timebinsize=$TW maketimecolumn=yes makeratecolumn=yes -V 0

title3 "epiclccorr"
epiclccorr srctslist=$path_out/${src}_lc_${frmtime}_src.lc eventlist=$clean_file outset=$path_out/${src}_lccorr_${frmtime}.lc bkgtslist=$path_out/${src}_lc_${frmtime}_bgd.lc withbkgset=yes applyabsolutecorrections=yes -V 0


sleep 1

title3 "lcstats"
lcstats cfile1="$path_out/${src}_lccorr_${frmtime}.lc" window=$path/${inst}_gti.wi dtnb=$frmtime nbint=1000000 tchat=2 logname="$path_out/${src}_xronos.log"
P=$(lcstats cfile1="$path_out/${src}_lccorr_${frmtime}.lc" window=$path/${inst}_gti.wi dtnb=$frmtime nbint=1000000 tchat=2 logname="$path_out/${src}_xronos.log" | grep "Prob of constancy")

sleep 5
P_chisq=$(echo $P | sed "s/Chi-Square Prob of constancy. //" | sed "s/ (0 means.*//")
P_KS=$(echo $P | sed "s/.*Kolm.-Smir. Prob of constancy //" |  sed "s/ (0 means.*//")

echo -e "Probabilities of constancy : \n\tP_chisq = $P_chisq\n\tP_KS    = $P_KS"

title3 "lcurve"

python3 -W"ignore" $scripts/lcurve.py -path /mnt/data/Florent/results -obs $observation -inst $inst -name $src -tw $TW -mode medium -pcs $P_chisq -pks $P_KS -n $id

end=`date +%s`
runtime=$((end-start))

###
# Writing output to files, ending script
###

echo -e > $path_out/${src}_region.txt "Source     = $srcexp\nBackground = $bgdexp\nTotal time = $runtime"
echo -e >> $output_log "$observation $id $src $inst $DL $TW $P_chisq $P_KS"

echo -e " # Total time obs. $observation : $runtime seconds"
echo -e "\nObservation $observation ended\nTotal time = $runtime seconds"
