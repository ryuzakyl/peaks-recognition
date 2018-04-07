#!/usr/bin/env
# -*- coding: utf-8 -*-
# Copyright (C) CENATAV, DATYS - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Victor M. Mendiola Lau <vmendiola@cenatav.co.cu>, March 2017

import os
import sys
from ctypes import (
    cdll,

    # c/c++ types declarations
    POINTER,
    c_int,
    c_double,

    # c/c++ functions declarations
    CFUNCTYPE,

    # for passing values as reference
    byref,

    # for mapping C structures in the wrapper
    Structure,
)

# common path for shared library
__shared_lib_path = "{}/peaks-analysis/cmake-build-debug/".format(os.path.split(__file__)[0])
lib_name = 'lib_peaks_analysis'

win32_lib_ext = '.dll'
posix_lib_ext = '.so'

# linux os support
if os.name == 'posix' and sys.platform.startswith('linux'):
    try:
        __peaks_analysis_lib_path = "{}{}{}".format(__shared_lib_path, lib_name, posix_lib_ext)
        __peaks_analysis_lib = cdll.LoadLibrary(__peaks_analysis_lib_path)
    except:
        raise ImportError('Error while loading COW shared library.')

# windows os support
elif os.name == 'nt':
    try:
        __peaks_analysis_lib_path = "{}{}{}".format(__shared_lib_path, lib_name, win32_lib_ext)
        __peaks_analysis_lib = cdll.LoadLibrary(__peaks_analysis_lib_path)
    except:
        raise ImportError('Error while loading COW shared library.')

# os not supported
else:
    raise NotImplemented()

# ---------------------------------------------------------------


# creates a c_array of type 'c_type' and size 'n' (if l is provided, then it copies the values of l)
def c_array(c_type, n, l=None):
    return (c_type * n)(*l) if l else (c_type * n)()


# allowing c/c++ function prototypes declarations a bit easier
def c_func(lib_func_name, lib_handle, ret_type, *args):
    # types and flags declarations
    a_types = []
    a_flags = []

    # for each argument
    for arg in args:
        a_types.append(arg[1])
        a_flags.append((arg[2], arg[0]) + arg[3:])

    return CFUNCTYPE(ret_type, *a_types)((lib_func_name, lib_handle), tuple(a_flags))


# subclassing the ctypes.Structure class to add new features
class _Structure(Structure):
    def __repr__(self):
        """
        Print the fields
        """
        res = []

        for field in self._fields_:
            res.append('%s=%s' % (field[0], repr(getattr(self, field[0]))))

        return self.__class__.__name__ + '(' + ','.join(res) + ')'

    @classmethod
    def from_param(cls, obj):
        """
        Magically construct from a tuple
        """
        if isinstance(obj, cls):
            return obj

        if isinstance(obj, tuple):
            return cls(*obj)

        raise TypeError


# represents the c# classic 'KeyValuePair' structure
class PeakInfo(_Structure):
    _fields_ = [
        ('lower_bound', c_int),
        ('upper_bound', c_int),
        ('height_index', c_int),
        ('peak_height', c_double),
        ('peak_area', c_double),
    ]


# additional type declarations
c_int_p = POINTER(c_int)  # c/c++ int* data type
c_double_p = POINTER(c_double)  # c/c++ double* data type
c_peak_info_p = POINTER(PeakInfo)  # c/c++ PeakInfo* data type

# ---------------------------------------------------------------


# handle to 'find_in_histogram' function in the shared library
__c_find_in_histogram = c_func(
    'find_in_histogram', __peaks_analysis_lib, c_peak_info_p,

    # histogram/signal/spectrum to perform detection on
    ('histogram', c_double_p, 1),  # double* histogram

    # histogram/signal/spectrum length
    ('h_length', c_int, 1),  # int h_length

    # interval size (dx) (size of interval of analysis I)
    ('dx', c_int, 1),  # int dx

    # indicates the "smoothness" of the curve
    ('smoothness', c_int, 1),  # int smoothness

    # growth angle of certain interval (indicates if the function is really growing)
    ('growth_angle', c_double, 1),  # double growth_angle

    # abate angle of certain interval (indicates if the function is really abating)
    ('abate_angle', c_double, 1),  # double abate_angle

    # threshold for filtering peaks that do not match required height
    ('height_thres', c_double, 1),  # double height_thres

    # out int for amount of peaks found
    ('peaks_count', c_int_p, 1),  # int* peaks_count
)

# handle to 'compute_peak_statistics' function in the shared library
__c_compute_peak_statistics = c_func(
    'compute_peak_statistics', __peaks_analysis_lib, PeakInfo,

    # histogram/signal/spectrum to perform detection on
    ('histogram', c_double_p, 1),  # double* histogram

    # indicates peak start
    ('lb', c_int, 1),  # int lb

    # indicates peak end
    ('ub', c_int, 1),  # int ub
)

# deletes an already allocated (PeakInfo*)
__c_delete_peak_info_ptr = c_func(
    'delete_peak_info_ptr', __peaks_analysis_lib, None,
    ('ptr', c_peak_info_p, 1)  # PeakInfo* int_ptr
)

# --------------------------------------------------


def delete_peak_info_ptr(ptr):
    # calling the c++ function
    __c_delete_peak_info_ptr(ptr)


# noinspection PyTypeChecker
def find_in_histogram(h, dx, smoothness, growth_angle, abate_angle, height_thres):
    # getting the length of the histogram
    h_length = len(h)

    # getting the ctypes array
    h_arr = c_array(c_double, h_length, h)

    # calling the c++ method
    peaks_count = c_int(0)  # peaks data size   (2 * amount of peaks)
    peaks_data = __c_find_in_histogram(h_arr, h_length, dx, smoothness, growth_angle, abate_angle, height_thres, byref(peaks_count))

    # copying the peaks data
    p_count = peaks_count.value
    peaks_info = [
        (
            peaks_data[i].lower_bound,
            peaks_data[i].upper_bound,
            peaks_data[i].height_index,
            peaks_data[i].peak_height,
            peaks_data[i].peak_area,

        )
        for i in range(p_count)
    ]

    # releasing the memory of 'peaks_data'
    delete_peak_info_ptr(peaks_data)

    # returning the peaks and valleys
    return peaks_info


def compute_peak_statistics(h, lb, ub):
    # getting the length of the histogram
    h_length = len(h)

    # getting the ctypes array
    h_arr = c_array(c_double, h_length, h)

    # calling the c++ method
    peak_stats = __c_compute_peak_statistics(h_arr, lb, ub)

    # returning peak stats as a tuple
    return (
        peak_stats.lower_bound,
        peak_stats.upper_bound,
        peak_stats.height_index,
        peak_stats.peak_height,
        peak_stats.peak_area,
    )
