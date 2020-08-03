#!/usr/bin/env python3
# coding=utf-8

########################################################################
#                                                                      #
# Variabilitectron - Searching variability into XMM-Newton data        #
#                                                                      #
# RENDERER functions to be used with the DETECTOR                      #
#                                                                      #
# Inés Pastor Marazuela (2018) - ines.pastor.marazuela@gmail.com       #
#                                                                      #
########################################################################
"""
Renderer's main programme
"""

# Built-in imports

from os.path import sys
import os
import shutil

# Third-party imports

from math import *
import numpy as np
import matplotlib
matplotlib.use("Pdf")
from matplotlib import colors, image, transforms, gridspec
import matplotlib.pyplot as plt
from pylab import figure, cm
from astropy import wcs
from astropy.io import fits
from astropy.table import Table


# Internal imports

import file_names as FileNames
from file_utils import *

def render_variability(var_file, output_file, sources=True, pars=None, maximum_value=None) :
    """
    Function rendering an from the matrix data.
    @param data: fits file containing variability and sources data
    @param sources: If the detected sources are plotted or not
    @param output_file: The path to the PDF file to be created
    @param pars: observation parameters
    @param maximum_value: The maximal value for the logarithmic scale
    """

    ###
    # Plot settings
    ###

    # Opening variability file
    hdulist = fits.open(var_file)

    data   = hdulist[0].data
    src    = hdulist[1].data
    header = hdulist[0].header

    hdulist.close()

    # Obtaining the WCS transformation parameters

    w = wcs.WCS(header)

    w.wcs.crpix = [header['REFXCRPX'], header['REFYCRPX']]
    w.wcs.cdelt = [header['REFXCDLT']/15, header['REFYCDLT']]
    w.wcs.crval = [header['REFXCRVL']/15, header['REFYCRVL']]
    w.wcs.ctype = [header['REFXCTYP'], header['REFYCTYP']]

    # Image limit
    dlim = [header['REFXLMIN'], header['REFXLMAX'], header['REFYLMIN'], header['REFYLMAX']]


    # Limite maximale de l'échelle des couleurs pour la normalisation par logarithme
    if maximum_value == None :
        maximum_value = max([max(tmp) for tmp in data])

    ###
    # Plotting
    ###

    # Plotting the variability data
    plt.subplot(111, projection=w)

    im = plt.imshow(data, cmap=cm.inferno, norm=colors.LogNorm(vmin=0.1, vmax=maximum_value), extent=dlim)

    ax = plt.gca()
    ax.set_facecolor('k')
    cbar = plt.colorbar(im)

    # Plotting the sources
    if sources :
        if len(src) != 0 :
            # Position of the sources
            plt.plot(src['X'], src['Y'], 'wo', alpha = 1, fillstyle='none')

    ra  = ax.coords[0]
    dec = ax.coords[1]

    ra.display_minor_ticks(True)
    dec.display_minor_ticks(True)
    ax.tick_params(axis='both', which='both', direction='in', color='w', width=1)

    # Labels
    plt.xlabel('RA', fontsize=10)
    plt.ylabel('DEC', fontsize=10)
    cbar.ax.set_ylabel('Variability', fontsize=10)

    # Title
    plt.title('OBS {0}   Inst: {1}'.format(header['OBS_ID'], header['INSTRUME']), fontsize=14)
    plt.text(0.5, 0.95, "TW {0} s    DL {1}   BS {2}".format(header['TW'], header['DL'], header['BS']),\
             color='white', fontsize=10, horizontalalignment='center', transform = ax.transAxes)

    plt.savefig(output_file, pad_inches=0, bbox_inches='tight', dpi=500)

########################################################################

def render_variability_all(var_file0, var_file1, var_file2, var_file3, output_file, sources=True, pars=None, maximum_value=10) :

    var_files = [var_file0, var_file1, var_file2, var_file3]

    # Starting loop on the different parameters
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(9.5,8))
    gs1 = gridspec.GridSpec(2, 2, wspace=0.05, hspace=0.05)

    for i in range(len(var_files)) :

        hdulist = fits.open(var_files[i])

        data   = hdulist[0].data
        src    = hdulist[1].data
        header = hdulist[0].header

        hdulist.close()

        # Obtaining the WCS transformation parameters

        w = wcs.WCS(header)

        w.wcs.crpix = [header['REFXCRPX'], header['REFYCRPX']]
        w.wcs.cdelt = [header['REFXCDLT']/15, header['REFYCDLT']]
        w.wcs.crval = [header['REFXCRVL']/15, header['REFYCRVL']]
        w.wcs.ctype = [header['REFXCTYP'], header['REFYCTYP']]

        # Image limit
        dlim = [header['REFXLMIN'], header['REFXLMAX'], header['REFYLMIN'], header['REFYLMAX']]

        # Plotting the variability data
        plt.subplot(gs1[i], projection=w)
        ax = plt.gca()
        im = plt.imshow(data/header['DL'], cmap=cm.inferno, norm=colors.LogNorm(vmin=0.1, vmax=maximum_value), extent=dlim)

        # Plotting the sources
        if sources :
            if len(src) != 0 :
                # Position of the sources
                plt.plot(src['X'], src['Y'], 'wo', alpha = 1, fillstyle='none')

        plt.text(0.5, 0.92, "TW {0} s    DL {1}   BS {2}".format(header['TW'], header['DL'], header['BS']),\
                 color='white', fontsize=10, horizontalalignment='center', transform = ax.transAxes)

        ra  = ax.coords[0]
        dec = ax.coords[1]

        if i > 1 :
            ra.set_axislabel('RA', fontsize=12)
        if i % 2 == 0 :
            dec.set_axislabel('DEC', fontsize=12)
        if i < 2 :
            ra.set_ticklabel_visible(False)
        if i % 2 != 0 :
            dec.set_ticklabel_visible(False)

        ra.display_minor_ticks(True)
        dec.display_minor_ticks(True)
        ax.tick_params(axis='both', which='both', direction='in', color='w', width=1)

        ax.set_facecolor('k')

    fig.subplots_adjust(right=0.77)
    cbar_ax = fig.add_axes([0.8, 0.11, 0.02, 0.77])
    cbar    = fig.colorbar(im, cax=cbar_ax)
    cbar.ax.set_ylabel('$\mathcal{V}$ / DL', fontsize=12)
    fig.suptitle('OBS {0}   Inst: {1}'.format(header['OBS_ID'], header['INSTRUME']), x=0.45, y = 0.93, fontsize=18)

    plt.savefig(output_file, pad_inches=0, dpi=500, bbox_inches='tight')


########################################################################
    
def render_variability_exodus(var_file0, var_file1, var_file2, output_file, corr_1, corr_2, corr_3, triple, sources=True, maximum_value=None) :
    """
    Function rendering an from the matrix data.
    @param var_file:    Fits file containing variability and sources data
    @param sources:     If the detected sources are plotted or not
    @param output_file: The path to the PDF file to be created
    @param corr_file:   Table with correlation between instruments
    @param triple:      List of triple correlation found betwwen the 3 EPIC
    @param maximum_value: The maximal value for the logarithmic scale
    """ 
    

    var_files = [var_file0, var_file1, var_file2]

    # Starting loop on the different parameters
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(9.5,5))
    gs1 = gridspec.GridSpec(1, 3, wspace=0.15)

    for i in range(len(var_files)) :

        hdulist = fits.open(var_files[i])

        data   = hdulist[0].data
        src    = hdulist[1].data
        header = hdulist[0].header

        hdulist.close()

        # Obtaining the WCS transformation parameters
        w = wcs.WCS(header)

        w.wcs.crpix = [header['REFXCRPX'], header['REFYCRPX']]
        w.wcs.cdelt = [header['REFXCDLT']/15, header['REFYCDLT']]
        w.wcs.crval = [header['REFXCRVL']/15, header['REFYCRVL']]
        w.wcs.ctype = [header['REFXCTYP'], header['REFYCTYP']]

        # Image limit
        dlim = [header['REFXLMIN'], header['REFXLMAX'], header['REFYLMIN'], header['REFYLMAX']]
        
        # Limite maximale de l'échelle des couleurs pour la normalisation par logarithme
        if maximum_value == None :
            maximum_value = max([max(tmp) for tmp in data])

        # Plotting the variability data
        plt.subplot(gs1[i], projection=w)
        ax = plt.gca()
        if i == 0:
            im = plt.imshow(data, cmap=cm.inferno, norm=colors.LogNorm(vmin=0.1, vmax=maximum_value), extent=dlim)
        else:
            im = plt.imshow(data*4, cmap=cm.inferno, norm=colors.LogNorm(vmin=0.1, vmax=maximum_value), extent=dlim)

        # Plotting the sources
        if sources :
            if len(src) != 0 :
                # Position of the sources
                for s in src:
                    plt.plot(s['X'], s['Y'], 'wo', alpha = 1, fillstyle='none', ms=s['RAWR'], zorder=1)
                    
                    if header['INSTRUME']=='EPN':
                        if s['ID'] in np.append(np.array(corr_1['ID_1']),np.array(corr_3['ID_1'])):
                            plt.plot(s['X'], s['Y'], 'bo', alpha = 1, fillstyle='none', ms=s['RAWR'], zorder=2)
                            for j in range(len(triple)):
                                if s['ID']==triple[j][0]:
                                    plt.plot(s['X'], s['Y'], 'go', alpha = 1, fillstyle='none', ms=s['RAWR'], zorder=3)
                                    
                    elif header['INSTRUME']=='EMOS1':
                        if s['ID'] in np.append(np.array(corr_1['ID_2']),np.array(corr_2['ID_1'])):
                            plt.plot(s['X'], s['Y'], 'bo', alpha = 1, fillstyle='none', ms=s['RAWR'], zorder=2)
                            for j in range(len(triple)):
                                if s['ID']==triple[j][2]:
                                    plt.plot(s['X'], s['Y'], 'go', alpha = 1, fillstyle='none', ms=s['RAWR'], zorder=3)
                                    
                    elif header['INSTRUME']=='EMOS2':
                        if s['ID'] in np.append(np.array(corr_2['ID_2']),np.array(corr_3['ID_2'])):
                            plt.plot(s['X'], s['Y'], 'bo', alpha = 1, fillstyle='none', ms=s['RAWR'], zorder=2)
                            for j in range(len(triple)):
                                if s['ID']==triple[j][4]:
                                    plt.plot(s['X'], s['Y'], 'go', alpha = 1, fillstyle='none', ms=s['RAWR'], zorder=3)

        plt.text(0.5, 0.92, "TW {0} s    DL {1}   BS {2}".format(header['TW'], header['DL'], header['BS']),\
                 color='white', fontsize=7, horizontalalignment='center', transform = ax.transAxes)
        plt.title('{0}'.format(header['INSTRUME']), fontsize=14)

        ra  = ax.coords[0]
        dec = ax.coords[1]

        ra.set_axislabel('RA', fontsize=12)
        dec.set_axislabel('DEC', fontsize=12)
        
        if i != 0 :
            dec.set_ticklabel_visible(False)

        ra.display_minor_ticks(True)
        dec.display_minor_ticks(True)
        ax.tick_params(axis='both', which='both', direction='in', color='w', width=1, labelsize=8)
        ax.set_facecolor('k')

    fig.subplots_adjust(right=0.77)
    cbar_ax = fig.add_axes([0.8, 0.27, 0.02, 0.45])
    cbar    = fig.colorbar(im, cax=cbar_ax)
    cbar.ax.set_ylabel('$\mathcal{V}$', fontsize=12)
    fig.suptitle('OBS {0}'.format(header['OBS_ID']), x=0.5, y = 0.85, fontsize=18)

    plt.savefig(output_file, pad_inches=0, dpi=500, bbox_inches='tight')


########################################################################

def ds9_renderer(var_file, reg_file) :
    """
    Function rendering variability with ds9
    @param var_file: variability fits file
    @param reg_file: region file
    """
    command = "ds9 {0} -scale linear -cmap bb -mode region -regionfile {1}".format(var_file, reg_file)
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
