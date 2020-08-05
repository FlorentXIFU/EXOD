#!/usr/bin/env python3
# coding=utf-8


########################################################################
#                                                                      #
# EXODUS - EPIC XMM-Newton Outburst Detector Ultimate System           #
#                                                                      #
# Rendering for exodus program                                         #
#                                                                      #
# Florent Castellani (2020) - castellani.flo@gmail.com                 #
#                                                                      #
########################################################################
"""
Page design and correlation checking for EXODUS program : Variability of
the 3 EPIC cameras
"""

import numpy as np
from astropy.io import fits
from astropy.table import Table

# Third-party imports
import argparse

# Internal imports
import file_names as FileNames
from exodus_utils import *
from renderer import render_variability_exodus

###
# Parsing arguments
###
parser = argparse.ArgumentParser()

# Variability parameters
parser.add_argument("-bs", help="Size of the detection box in pixel.", type=int)
parser.add_argument("-dl", help="The number of times the median variability is required to trigger a detection.", type=float)
parser.add_argument("-tw", help="The duration of the time windows.", type=float)
parser.add_argument("-gtr", help="Ratio of acceptability for a time window. Shall be between 0.0 and 1.0.", type=float)

# Path to files
parser.add_argument("-path", help="Path to the folder containing the observation files", type=str)
parser.add_argument("-out", help="Name of the output file", default=FileNames.OUTPUT_EXODUS, type=str)

args = parser.parse_args()

# Modifying arguments
if args.path[-1] != '/' :
    args.path = args.path + '/'
    
out = args.path + 'variability_{}_{}_{}_{}_'.format(int(args.dl), int(args.tw), args.bs, args.gtr) + "all_inst.pdf"

# Defining paths to files
file0 = args.path + '{}_{}_{}_{}_PN/'.format(int(args.dl), int(args.tw), args.bs, args.gtr) + FileNames.VARIABILITY
file1 = args.path + '{}_{}_{}_{}_M1/'.format(int(args.dl), int(args.tw), args.bs, args.gtr) + FileNames.VARIABILITY
file2 = args.path + '{}_{}_{}_{}_M2/'.format(int(args.dl), int(args.tw), args.bs, args.gtr) + FileNames.VARIABILITY

###
# Computing source lists and correlation for all EPIC instruments
###


# PN source list
hdulist = fits.open(file0)
src_PN = Table(hdulist[1].data)
hdulist.close()
# MOS 1 source list
hdulist = fits.open(file1)
src_M1 = Table(hdulist[1].data)
hdulist.close()
# MOS 2 source list
hdulist = fits.open(file2)
src_M2 = Table(hdulist[1].data)
hdulist.close()

# Checking correlation between lists

# Implementing correlation table
corr_table = Table(names=('ID_1', 'INST_1', 'RA_1', 'DEC_1', 'R_1','ID_2', 'INST_2', 'RA_2', 'DEC_2', 'R_2')\
                   , dtype=('i2', 'U25', 'f8', 'f8', 'f8','i2', 'U25', 'f8', 'f8', 'f8'))

# Checking correlation for the 3 EPIC
check_correlation(src_PN, src_M1, corr_table)
check_correlation(src_M1, src_M2, corr_table)
check_correlation(src_PN, src_M2, corr_table)

# Sorting the table
corr_PN_M1 = corr_table[np.where((corr_table['INST_1']=='PN') & (corr_table['INST_2']=='M1'))]
corr_M1_M2 = corr_table[np.where((corr_table['INST_1']=='M1') & (corr_table['INST_2']=='M2'))]
corr_PN_M2 = corr_table[np.where((corr_table['INST_1']=='PN') & (corr_table['INST_2']=='M2'))]

# Printing results
if len(corr_PN_M1) !=0:
    print("\n Correlation between EPIC-pn and EPIC-MOS1 \n")
    print(corr_PN_M1)

if len(corr_M1_M2) !=0:
    print("\n Correlation between EPIC-MOS1 and EPIC-MOS2 \n")
    print(corr_M1_M2)
    
if len(corr_PN_M2) !=0:
    print("\n Correlation between EPIC-pn and EPIC-MOS2 \n")
    print(corr_PN_M2)

src_triple = []
if len(corr_PN_M1) !=0 and len(corr_M1_M2) !=0 and len(corr_PN_M2) !=0:
    src_triple = check_triple(corr_PN_M1, corr_M1_M2, corr_PN_M2)

if len(src_triple) !=0:
    print("\n Correlation between the 3 EPIC detectors \n")
    print(src_triple)
    
    # Writing triple correlation file for lightcurve exodus
    triple_f = open(args.path + 'triple_correlation.txt', 'w')
    text = ''
    for s in src_triple:
        text = text + '{0} {1} {2} {3} {4} {5}\n'.format(s[0], s[1], s[2], s[3], s[4], s[5])
        
    triple_f.write(text)
    triple_f.close()
    


###
# Applying renderer
###

render_variability_exodus(file0, file1, file2, out, corr_PN_M1, corr_M1_M2, corr_PN_M2, src_triple)

print("\n" + out)
