README
=======

MakeFile
---------

Make a distribution with executable using guidata disthelper and setup.py

    make dist

To make the installer for release:

    make installer

LM\_ratio\_installer.iss is the installer file for use with [Inno Setup 5.][inno] The `compil32` command must be on your path (located in Inno Setup 5 program file directory).

Clean old files with:
    
    make clean

[inno]: http://www.jrsoftware.org/isinfo.php

Additional info
----------------

LEDspectra is new measurement (4/9/2014) with background subtracted and quantally corrected.

To change the LED spectra, find the LM ratio directory in your program files and replace LEDspectra.xlsx, located in the dat subdirectory. Make sure you do not change the name of LEDspectra.xlsx. 

**WARNING: Do not do this unless you are certain you understand the consequences!**
