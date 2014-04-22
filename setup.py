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

import base
import appdirs

Info = git.Repo()
    
def create_executable():
    """Build executable using ``guidata.disthelpers``"""
    dist = Distribution()
    dist.setup(name="LM ratio", version="0.2",
               description=u"A gui for computing LM ratio",
               script="gui_LMratio.py", target_name="LMratio.exe")
    dist.add_data_file('dat')
    dist.add_data_file('lm_ratiorc.txt')
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
