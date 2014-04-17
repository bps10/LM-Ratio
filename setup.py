# -*- coding: utf-8 -*-
#
# Copyright © 2014 Brian Schmidt
# Licensed under the terms of the MIT License

"""Create a stand-alone executable"""

try:
    from guidata.disthelpers import Distribution
except ImportError:
    raise ImportError, "This script requires guidata 1.4+"

import spyderlib
import git as git

import sys
sys.path.append("C:/Users/Brian/Documents/Projects")
sys.path.append("C:/Python27/Lib/lib-tk")
import base

Info = git.Repo()
    
def create_executable():
    """Build executable using ``guidata.disthelpers``"""
    dist = Distribution()
    dist.setup(name="LM ratio", version="0.1",
               description=u"A gui for computing LM ratio",
               script="gui_LMratio.py", target_name="LMratio.exe")
               
    #spyderlib.add_to_distribution(dist)
    dist.add_data_file('LEDspectra.csv')
    dist.add_modules('guidata')
    dist.add_modules('guiqwt')
    dist.add_matplotlib()
    dist.includes += ['scipy.sparse.csgraph._validation']
    dist.includes += ['scipy.sparse.linalg.dsolve.umfpack']
    dist.excludes += ['IPython']
    # Building executable
    dist.build('cx_Freeze', cleanup=True)


if __name__ == '__main__':
    create_executable()
