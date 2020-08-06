#!/usr/bin/env python3
# coding=utf-8

########################################################################
#                                                                      #
# EXODUS - Searching for fast transients into XMM-Newton data          #
#                                                                      #
# Generating lightcurve plots for trile correlation                    #
#                                                                      #
# Florent Castellani  (2020) -   castellani.flo@gmail.com              #
#                                                                      #
########################################################################


# Built-in imports

from math import *
from os import path
from os.path import sys

# Third-party imports

import argparse
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.ticker import FormatStrFormatter
from scipy.stats import binned_statistic
from astropy.io import fits

###
# Parsing arguments
###

parser = argparse.ArgumentParser()
parser.add_argument("-path", dest="path", help="Path to the observation files", nargs='?', type=str)
parser.add_argument("-name", dest="name", help="Source name", nargs='?', type=str)
parser.add_argument("-obs", help="Observation identifier", nargs='?', type=str, default="")
parser.add_argument("-inst", help="Type of detector", nargs='?', type=str, default="PN")
parser.add_argument("-src", help="Path to the source's lightcurve fits file", nargs='?', type=str, default=None)
parser.add_argument("-bgd", help="Path to the background's lightcurve fits file", nargs='?', type=str, default=None)
parser.add_argument("-gti", help="Path to the GTI of the observation", nargs='?', type=str, default=None)
parser.add_argument("-tw", help="Time window", nargs='?', type=int, default=100)
parser.add_argument("-n", help="Lightcurve number", nargs='?', type=str, default="")
parser.add_argument("-pcs", dest="pcs", help="Chi-square probability of constancy", nargs='?', type=float, default=None)
parser.add_argument("-pks", dest="pks", help="Kolmogorov-Smirnov probability of constancy", nargs='?', type=float, default=None)
parser.add_argument("-mode", dest="mode", help="Plot style: monochrome / medium / color", nargs='?', type=str, default="medium")
args = parser.parse_args()

###
# Defining variables
###