"""
A few utility functions to be used in boxplot viz.
"""

import numpy as np
import pandas as pd


def get_bplot_inputs(df, groups_ls, metab, group_colname="Label"):
    """Get boxplot inputs from a dataframe
    
    PARAMS
    ------
    df: input abundance dataframe of shape (n_samples, n_metabs + 2). First 2 columns are sample name and group labels.
    groups_ls: list of groups (str) available in df. 
    metab: str; specific metabolite in df to get boxplot data.
    group_colname: str; column name of the `group` column.
    
    RETURNS
    -------
    plot_input_arr: list of sublists of data to be plot in a boxplot. 
    The sublists need not be of the same length.
    """
    plot_input_arr = []
    for grp in groups_ls:
        arr = list(df.loc[(df[group_colname]==grp)][metab])
        plot_input_arr.append(arr)

    return plot_input_arr


def batch_metabs(input_arr, batch_size=5):
    """Batches up a list of things into a list of sublists, where each sublist is of length batch_size.
    Any remainder is appended to the end of the list of sublist. 
    
    PARAMS
    ------
    input_arr: list of any object, though usually str.
    batch_size: int; size of sublist.
    
    RETURNS
    -------
    batches_ls: list of sublists.
    """
    batches_ls = []
    for i in range(0, len(input_arr), batch_size):
        batch = input_arr[i:i+batch_size]
        batches_ls.append(batch)
        
    return batches_ls