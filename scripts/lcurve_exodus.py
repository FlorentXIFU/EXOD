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
from matplotlib import rcParams, gridspec
from matplotlib.ticker import FormatStrFormatter
from scipy.stats import binned_statistic
from astropy.io import fits

###
# Parsing arguments
###

parser = argparse.ArgumentParser()
parser.add_argument("-path", dest="path", help="Path to the observation files", nargs='?', type=str)
parser.add_argument("-obs", help="Observation identifier", nargs='?', type=str, default="")
parser.add_argument("-file", help="File with source names and probabilities", nargs='?', type=str, default="")
parser.add_argument("-tw", help="Time window", nargs='?', type=int, default=100)
parser.add_argument("-ipn", help="num source PN", nargs='?', type=str, default="")
parser.add_argument("-im1", help="num source M1", nargs='?', type=str, default="")
parser.add_argument("-im2", help="num source M2", nargs='?', type=str, default="")
args = parser.parse_args()

###
# Defining variables
###

# Path
if args.path[-1] == '/' :
    args.path = args.path[:-1]
    
# Extracting parameters from inter file
with open(args.file, "r") as f:
    for line in f:
        words=line.split()
        if words[3]=='PN':
            name_PN=words[2]     # Source name
            P_chi_PN=words[6]   # Chi-square probability of constancy
            P_KS_PN=words[7]    # Kolmogorov-Smirnov probability of constancy
        elif words[3]=='M1':
            name_M1=words[2]
            P_chi_M1=words[6]
            P_KS_M1=words[7]
        elif words[3]=='M2':
            name_M2=words[2]
            P_chi_M2=words[6]
            P_KS_M2=words[7]
            
# Source and background files
# PN
lccorr_PN = '{0}/{1}/lcurve_{2}_PN/{3}_lccorr_{2}.lc'.format(args.path, args.obs, args.tw, name_PN)
bgd_PN = None
if path.exists(lccorr_PN) :
    src_PN = lccorr_PN
else : 
    src_PN = '{0}/{1}/lcurve_{2}_PN/{3}_lc_{2}_src.lc'.format(args.path, args.obs, args.tw, name_PN)
    bgd_PN = '{0}/{1}/lcurve_{2}_PN/{3}_lc_{2}_bgd.lc'.format(args.path, args.obs, args.tw, name_PN)
# MOS1
lccorr_M1 = '{0}/{1}/lcurve_{2}_M1/{3}_lccorr_{2}.lc'.format(args.path, args.obs, args.tw, name_M1)
bgd_M1 = None
if path.exists(lccorr_M1) :
    src_M1 = lccorr_M1
else : 
    src_M1 = '{0}/{1}/lcurve_{2}_M1/{3}_lc_{2}_src.lc'.format(args.path, args.obs, args.tw, name_M1)
    bgd_M1 = '{0}/{1}/lcurve_{2}_M1/{3}_lc_{2}_bgd.lc'.format(args.path, args.obs, args.tw, name_M1)
# MOS2
lccorr_M2 = '{0}/{1}/lcurve_{2}_M2/{3}_lccorr_{2}.lc'.format(args.path, args.obs, args.tw, name_M2)
bgd_M2 = None
if path.exists(lccorr_M2) :
    src_M2 = lccorr_M2
else : 
    src_M2 = '{0}/{1}/lcurve_{2}_M2/{3}_lc_{2}_src.lc'.format(args.path, args.obs, args.tw, name_M2)
    bgd_M2 = '{0}/{1}/lcurve_{2}_M2/{3}_lc_{2}_bgd.lc'.format(args.path, args.obs, args.tw, name_M2)

# GTI files
gti_PN = '{0}/{1}/PN_gti.fits'.format(args.path, args.obs)
gti_M1 = '{0}/{1}/M1_gti.fits'.format(args.path, args.obs)
gti_M2 = '{0}/{1}/M2_gti.fits'.format(args.path, args.obs)

# Name of sources
name_PN=name_PN.replace("_", "+")
name_M1=name_M1.replace("_", "+")
name_M2=name_M2.replace("_", "+")

# Output file
out='{0}/{1}/triple_PN_{2}_M1_{3}_M2_{4}_variability.pdf'.format(args.path, args.obs, int(args.ipn), int(args.im1), int(args.im2))

# Putting in lists
src_list  = [src_PN, src_M1, src_M2]
bgd_list  = [bgd_PN, bgd_M1, bgd_M2]
inst_list = ['PN', 'M1', 'M2']
name_list = [name_PN, name_M1, name_M2]
gti_list  = [gti_PN, gti_M1, gti_M2]
pcs_list  = [float(P_chi_PN), float(P_chi_M1), float(P_chi_M2)]
pks_list  = [float(P_KS_PN), float(P_KS_M1), float(P_KS_M2)]
id_list   = [int(args.ipn), int(args.im1), int(args.im2)]

# Subplot
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(25,5))
gs1 = gridspec.GridSpec(1, 3, wspace=0.3)

#seaborn-colorblind
color = ['#01b4bc', '#009E73', '#D55E00', '#fa5457', '#f6d51f', '#56B4E9']
rcParams['font.family'] = 'serif'

###
# Starting loop for plotting
###

for s in range(3) :
    ###
    # Extracting information from fits files
    ###
    
    hdu_src = fits.open(src_list[s])
    data_src    = hdu_src[1].data
    head_src    = hdu_src[1].header
    hdu_src.close()

    cts  = data_src[:]['RATE']
    time = data_src[:]['TIME']
    std  = data_src[:]['ERROR']

    tstart = head_src['TSTART']
    tstop  = head_src['TSTOP']
    t0     = time[0]
    tf     = time[-1]
    time   = time - tstart
    
    # Background
    if bgd_list[s] != None :
        hdu_bgd = fits.open(bgd_list[s])
        data_bgd    = hdu_bgd[1].data
        head_bgd    = hdu_bgd[1].header
        hdu_bgd.close()

        cts_bgd  = data_bgd[:]['RATE']
        time_bgd = data_bgd[:]['TIME']
        std_bgd  = data_bgd[:]['ERROR']

        for t_s in range(len(time)) :
            for t_b in range(len(time_bgd)) :
                if time[t_s] == time_bgd[t_s] :
                    cts[t_s] == cts[t_s] - cts_bgd[t_b]

    # GTI
    hdulist_gti = fits.open(gti_list[s])
    data_gti    = hdulist_gti[1].data
    hdulist_gti.close()

    start = data_gti[:]['START']
    stop  = data_gti[:]['STOP']

    #time_bgd  = time_bgd - tstart
    if len(data_gti) > 1 :
        start_gti = np.insert(stop, 0, tstart) - tstart
        stop_gti  = np.insert(start, len(data_gti), tstop) - tstart
    elif len(data_gti) == 0 :
        start_gti = np.array([tstart])
        stop_gti  = np.array([tstop])
    else :
        start_gti = np.array([])
        stop_gti  = np.array([])

    # GTI inclusion
    if len(start_gti) > 0 :
        for i in range(len(start_gti)) :
            cdt  = np.where((time > start_gti[i]) & (time < stop_gti[i]))
            cts  = np.delete(cts, cdt)
            time = np.delete(time, cdt)
            std  = np.delete(std, cdt)

    cdt  = np.where(np.isfinite(cts) == True)
    time = time[cdt]
    cts  = cts[cdt]
    std  = std[cdt]

    for i in range(len(cts)) :
        if cts[i] < 0 :
            cts[i] = 0

    time = time[cts != 0]
    std  = std[cts != 0]
    cts  = cts[cts != 0]

    # Max, min, etc
    xmin = time[0]
    xmax = time[-1]
    ymin = 0
    ymax = np.max(cts + std)

    max = np.argmax(cts)    # Argument of the max
    min = np.argmin(cts)    # Argument of the min
    med = np.median(cts)

    if cts[max] - med > med - cts[min] :
        var = max - med
        index   = max
        var_min = med/(ymax-ymin) - ymin/(ymax-ymin)
        var_max = cts[index]/(ymax-ymin) - ymin/(ymax-ymin)
        label = "Maximum"
    else :
        var = med - min
        index   = min
        var_min = cts[index]/(ymax-ymin) - ymin/(ymax-ymin)
        var_max = med/(ymax-ymin) - ymin/(ymax-ymin)
        label   = "Minimum"
    ###
    # Plotting
    ###
    
    # Plotting the lightcurves
    plt.subplot(gs1[s])
    ax = plt.gca()
    #im = plt.imshow(data/header['DL'], cmap=cm.inferno, norm=colors.LogNorm(vmin=0.1, vmax=maximum_value), extent=dlim)

    # Data
    plt.plot(time, cts, "o-", linewidth=0.7, markersize=2, color='k', label="Source",zorder=2)
    plt.fill_between(time, cts - std, cts + std, alpha=0.3, color='c', zorder=2)
    # Max/min, median
    plt.axhline(med, xmin=0, xmax=1, linestyle='--', color='#54008c', linewidth=1, zorder=4, label="Median")
    plt.axhline(cts[index], xmin=0, xmax=1, linestyle=':', color='#54008c', linewidth=1, zorder=4, label=label)
    # GTI
    if len(data_gti) > 1 :
        for i in range(len(data_gti)) :
            mpl.rcParams['hatch.linewidth'] = 0.1
            ax.axvspan(start_gti[i], stop_gti[i], facecolor= 'k', alpha=0.2, edgecolor='None', zorder=1)

    # Labels
    #plt.legend(loc='upper right', fontsize=10)
    plt.xlabel("Time (s)", fontsize=16)
    plt.ylabel("counts s$^{-1}$", fontsize=16)

    # Title
    # Info
    plt.text(0.03, 1.1, "id : {0}".format(id_list[s]), transform = ax.transAxes, fontsize=13)
    plt.text(0.2, 1.1, "inst : {0}".format(inst_list[s]), transform = ax.transAxes, fontsize=13)
    plt.text(0.5, 1.1, "src : {0}".format(name_list[s]), transform = ax.transAxes, fontsize=13)
    # Probabilities of constancy
    plt.text(0.1, 1.03, r"P($\chi^2$) = {0:.2e} ".format(pcs_list[s]), transform = ax.transAxes, fontsize=13)
    plt.text(0.52, 1.03, r"P(KS) = {0:.2e} ".format(pks_list[s]), transform = ax.transAxes, fontsize=13)

    # Setup
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    plt.minorticks_on()
    ax.yaxis.set_ticks_position('both')
    ax.xaxis.set_ticks_position('both')
    plt.tick_params(axis='both', which='both', direction='in', labelsize=14)
    plt.savefig(out, pad_inches=0, bbox_inches='tight')
    #plt.show()

fig.subplots_adjust(right=0.77)
fig.suptitle('OBS {0}'.format(args.obs), x=0.45, y = 1.1, fontsize=25)

plt.savefig(out, pad_inches=0, dpi=500, bbox_inches='tight')
print(out)