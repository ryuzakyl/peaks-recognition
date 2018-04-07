#!/usr/bin/env
# -*- coding: utf-8 -*-
# Copyright (C) CENATAV, DATYS - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Victor M. Mendiola Lau <vmendiola@cenatav.co.cu>, March 2017

import os
import pandas as pd
from peaks_analysis import find_in_histogram, compute_peak_statistics

# visualization
import pylab
import matplotlib
matplotlib.style.use('ggplot')


def demo_auto_detect_peaks():
    print('Peak auto detection and characterization...')

    # defining sample path
    data_path = "{}/data/sample.csv".format(os.path.split(__file__)[0])

    # loading sample from file
    df = pd.read_csv(data_path, header=None)

    # getting histogram/signal/spectrum data
    X = df[0].tolist()
    Y = df[1].tolist()

    # automatic detection parameters
    dx = 15
    smoothness = 5
    growth_angle = 15.0
    abate_angle = -15.0
    height_thres = 40
    print('Detection parameters: (dx={}, smooth={}, growth={}, abate={})'.format(dx, smoothness, growth_angle, abate_angle))

    # finding peaks in histogram
    peaks_info = find_in_histogram(Y, dx, smoothness, growth_angle, abate_angle, height_thres)

    # plotting histogram/signal/spectrum
    pylab.plot(X, Y)

    # getting retention times of peaks
    peaks_rt = [(X[lb], X[ub], X[hi], ph, pa) for lb, ub, hi, ph, pa in peaks_info]

    # drawing detection
    for i, (lb, ub, hi, ph, pa) in enumerate(peaks_rt):
        # drawing detected peaks
        pylab.axvline(x=lb, linewidth=1, color='green')
        pylab.axvline(x=ub, linewidth=1, color='black')

        # printing peak info
        print('{} - (lb={}, ub={}, hi={}, ph={}, pa={})'.format(i + 1, lb, ub, hi, ph, pa))

    # showing figures
    pylab.show()


def demo_compute_stats_from_peak():
    print('Peak characterization...')

    # defining sample path
    data_path = "{}/data/sample.csv".format(os.path.split(__file__)[0])

    # loading sample from file
    df = pd.read_csv(data_path, header=None)

    # getting histogram/signal/spectrum data
    X = df[0].tolist()
    Y = df[1].tolist()

    lb = 17444
    ub = 17640

    # computing peak statistics
    peak_stats = compute_peak_statistics(Y, lb, ub)

    # printing results
    print("(lb={}, ub={}, hi={}, ph={}, pa={})".format(X[peak_stats[0]], X[peak_stats[1]], X[peak_stats[2]], peak_stats[3], peak_stats[4]))


if __name__ == '__main__':
    # performs peak auto-detection on a histogram/signal/spectrum and plots the results
    demo_auto_detect_peaks()

    print()
    print('------------------------------')
    print()

    # performs peak encoding by means of several statistics
    demo_compute_stats_from_peak()
