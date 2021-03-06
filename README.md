# README

_LM ratio is a program written for computing L:M cone ratios from electroretinogram (ERG) flicker photometry data. It was developed for use with a custom designed ERG system in the Neitz laboratories._

## Installation

Download the latest [release][_release] and follow the installation instructions. 

Currently only Windows 64 bit platforms are supported. The program has been tested on Windows 7, but is expected to work on other modern Windows versions as well. 

Please file a [report][issues] if you encounter problems with the installation.

[issues]: https://github.com/bps10/LM-Ratio/issues
[_release]: https://github.com/bps10/LM-Ratio/releases

## Basic usage

This program computes L:M cone ratio using 7 pieces of information: age, peak L cone sensitivity (nm), peak M cone sensitivity (nm), and the intensity of the reference and 3 test LEDs used in the flicker photometry. The ID of the subject is also required for the purposes of saving results.

The data necessary to run the program can either be inputed manually (simply type the values into the text boxes) or loaded from a csv file. 

A csv file should have two columns with names of the parameters in the left hand column and values in the right hand column. [This][example1] is an example of a data file with complete information. If this file is selected, the program will load in all of the information in the csv and fill in the appropriate boxes. The only remaining information required from the user is the subject ID. 

Alternatively, a csv file with only partial information can also be loaded: [example 2][example2]. In this case, only the fields contained in the csv will be filled in and the user will need to provide the additional information, in this case, peak L, peak M, age and ID.

[Example 2][example2] also demonstrates the case when multiple measurements exist. Typically each test light is measured 3-5 times. The LM ratio program will load all of these measurements and the mean will be used for computing LM ratio.

[example1]: https://github.com/bps10/LM-Ratio/blob/master/dat/subject_1.csv
[example2]: https://github.com/bps10/LM-Ratio/blob/master/dat/subject_2.csv

### Results

In the white box on the bottom right of the gui, results from the computation will be printed. The values printed are the subject ID, %L, %M and error. %L is a linear representation of L:M cone ratio, L / (L+M) * 100. %M is simply 100 - %L. L:M cone ratio can be computed by %L / %M. Error is the root mean squared error of the fitted line to the data. Though the data are plotted in logarithmic coordinates, the fitting is done in linear coordinates. Therefore, the error is reported in sensitivity, which is on a scale from 0 to 1.

### Saving

After inputing all data fields and clicking analyze, you can then click the 'save' button to save the results. This action will write the data to a csv file and save the figure as a png and eps file. The output will be saved into a directory named by the subject ID within the specified save location (see below). Data will never be overwritten. If a file with the subject's ID already exists, a number will be appended to the csv and image files to ensure that they remain unique.

If the saving process is successful, a message will be displayed beneath the subject's results indicating that everything has saved. If instead an error has occurred, a message indicating so will be displayed. It is recommended that you close the program and begin again if you see this error. If this problem persists, please file an issue.

### Data structure format

The results generated by the program are saved in csv files. All parameters necessary to recompute the results are saved in these files. The same conventions used with input data, discussed above, are maintained for the results as well.

### Save location

The default save location is `C:\Users\Public\Documents\<subject ID>`. A user can change the save location by selecting File -> Change save dir and selecting a new directory to save files. This will now be the default save location for the current and future LM ratio sessions until a new location is chosen.

## Dev

### MakeFile

Make a distribution with executable using guidata disthelper and setup.py

    make dist

To make the installer for release:

    make installer

LM\_ratio\_installer.iss is the installer file for use with [Inno Setup 5.][inno] The `compil32` command must be on your path (located in Inno Setup 5 program file directory).

Clean old files with:
    
    make clean

[inno]: http://www.jrsoftware.org/isinfo.php

## License

This software is issued under an [MIT License][license].

[license]: https://github.com/bps10/LM-Ratio/blob/master/LICENSE.txt

## Additional info

LEDspectra is new measurement (4/9/2014) with background subtracted and quantally corrected.

To change the LED spectra, find the LM ratio directory in your program files and replace LEDspectra.xlsx, located in the dat subdirectory. Make sure you do not change the name of LEDspectra.xlsx. 

**WARNING: Do not do this unless you are certain you understand the consequences!**
