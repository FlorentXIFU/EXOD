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

# Third-party imports
import argparse

# Internal imports
import file_names as FileNames
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
args.out = args.path + args.out

# Dd=efining paths to files

file0 = args.path + '{}_{}_{}_{}_PN/'.format(int(args.dl), int(args.tw), args.bs, args.gtr)   + FileNames.VARIABILITY
file1 = args.path + '{}_{}_{}_{}_M1/'.format(int(args.dl), int(args.tw), args.bs, args.gtr)   + FileNames.VARIABILITY
file2 = args.path + '{}_{}_{}_{}_M2/'.format(int(args.dl), int(args.tw), args.bs, args.gtr)   + FileNames.VARIABILITY

###
# Applying renderer
###

render_variability_exodus(file0, file1, file2, args.out)

print(args.out)