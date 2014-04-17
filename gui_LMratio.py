from __future__ import division
from guidata.qt.QtGui import (QFont, QSplitter, QMainWindow, 
    QListWidget, QPushButton, QFileDialog, QDialog)
from guidata.qt.QtCore import QSize, Qt, SIGNAL
from guidata.dataset.qtwidgets import DataSetEditGroupBox
from guidata.configtools import get_icon
from guidata.qthelpers import create_action, add_actions, get_std_icon

from guiqwt.plot import CurveDialog, CurveWidget
from guiqwt.builder import make
from guidata.dataset.datatypes import DataSet
from guidata.dataset.dataitems import FloatItem, StringItem

import numpy as np
import sys, os
from analyze_LMratio import LMratio
from base import spectsens as spect
from base import optics as o


class Param(DataSet):
    name = StringItem(("name"), default=("sample"))
    age = FloatItem(label='age', default=26)
    lpeak = FloatItem(label='peak L', default=559)
    mpeak = FloatItem(label='peak M', default=530)
    data0 = FloatItem(label='ref LED', default=10)
    data1 = FloatItem(label='LED1')
    data2 = FloatItem(label='LED2')
    data3 = FloatItem(label='LED3')


class CentralWidget(QSplitter):
    def __init__(self, parent):
        QSplitter.__init__(self, parent)

        self.setContentsMargins(10, 10, 10, 10)
        self.setOrientation(Qt.Vertical)

        # set up left side of the bottom panel        
        self.properties = DataSetEditGroupBox(("Properties"), Param,
             button_text='OK')
        self.properties.setEnabled(True)
        self.connect(self.properties, SIGNAL("apply_button_clicked()"),
                     self.properties_changed)
        self.load_button = QPushButton('load data', self.properties)
        self.load_button.clicked.connect(self.load) 

        # add left side of the bottom panel
        left_side = QSplitter()
        left_side.setOrientation(Qt.Vertical)
        left_side.addWidget(self.load_button)
        left_side.addWidget(self.properties)

        # set up right side of the bottom panel
        self.results = QListWidget(self)
        self.save_button = QPushButton('save', self.results)
        self.save_button.clicked.connect(self.save)  

        # add right side of the bottom panel
        right_side = QSplitter()
        right_side.setOrientation(Qt.Vertical)
        right_side.addWidget(self.results)
        right_side.addWidget(self.save_button)
        self.addWidget(right_side) 

        # add left and right side to bottom
        bottom = QSplitter()
        bottom.addWidget(left_side)
        bottom.addWidget(right_side)

        self.plots = CurveWidget(self, 
            xlabel='wavelength (nm)', ylabel='sensitivity')

        self.addWidget(self.plots)
        self.addWidget(bottom)

        self.age = 26
        self.peakL = 559
        self.peakM = 530
        self.ref_LED = 10
        self.LED1 = 15
        self.LED2 = 13.9
        self.LED3 = 40.45
        self.L_OD = 0.35
        self.M_OD = 0.22
        self.show_data(PRINT=False)    

        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        self.setHandleWidth(10)
        self.setSizes([800, 1])

    def load(self):
        '''
        '''
        # Open a file finder. Load the csv file.
        name = QFileDialog.getOpenFileName()
        f = open(name, 'r')
        raw_dat = f.read()
        f.close()

        data = {}
        lines = raw_dat.split('\n')
        for line in lines:
            if line != '':
                stuff = line.split(',')
                data[stuff[0]] = float(stuff[1])

        if 'name' in data:
            self.properties.dataset.name = data['name']
        if 'age' in data:
            self.properties.dataset.age = data['age']
        if 'L_peak' in data:
            self.properties.dataset.lpeak = data['L_peak']
        if 'M_peak' in data:
            self.properties.dataset.mpeak = data['M_peak']
        if 'ref' in data:    
            self.properties.dataset.data0 = data['ref']
        if 'LED1' in data:   
            self.properties.dataset.data1 = data['LED1']
        if 'LED2' in data:
            self.properties.dataset.data2 = data['LED2']
        if 'LED3' in data:
            self.properties.dataset.data3 = data['LED3']


    def save(self):
        '''
        '''
        self.properties_changed()
        self.show_data(save_plot=True, save_data=True, PRINT=True)
        message = []
        message.append('Plot saved.')
        self.results.addItems(message) 

    def show_data(self, save_plot=False, save_data=False, PRINT=True):
        '''
        '''
        LM = LMratio()
        LM.set_parameters(age=self.age, L_peak=self.peakL, 
            M_peak=self.peakM)
        LM.set_LED_rel_intensities(ref=self.ref_LED, 
            light1=self.LED1, 
            light2=self.LED2, 
            light3=self.LED3)
        l_frac, error = LM.find_LMratio(PRINT=False)
        l_percent = l_frac * 100

        _data = LM.return_data()
        data_x = _data['LED_peaks']
        data_y = np.log10(
            np.array([_data['ref'], _data[1], _data[2], _data[3]]))
        # get fit

        spectrum = LM.return_spectrum()
        cones = LM.return_cones()
        fit = np.log10(LM.return_fit())
        L_cones = np.log10(cones['L'])
        M_cones = np.log10(cones['M'])

        items = (make.curve(spectrum, L_cones, 'L cones', 
                    color='r', linewidth=2),
                make.curve(spectrum, M_cones, 'M cones',
                    color='g', linewidth=2),
                make.curve(spectrum, fit, 'fit',
                    color='k', linewidth=2),
                make.curve(data_x, data_y, linestyle='NoPen',
                    marker="Diamond", markersize=14, markerfacecolor='k')
                )
        self.plots.plot.del_all_items()
        for item in items:
            self.plots.plot.add_item(item)
        self.plots.plot.set_plot_limits(450, 670, -2, 0)
        self.plots.plot.replot()

        if PRINT:

            message = [self.name]
            message.append('L: ' + str(round(l_percent, 1)))
            message.append('M: ' + str(round(100 - l_percent, 2)))
            message.append('error: ' + str(round(error, 4)))
            self.results.clear()
            self.results.addItems(message) 

        if save_plot or save_data:
            directory = 'C:\Users\Public\Documents\\' + self.name + '\\'
            if not os.path.exists(directory):
                os.makedirs(directory)

            trial = 1
            file_name = directory + self.name + '_' + str(trial)
            while os.path.exists(file_name + '.csv'):
                trial += 1
                file_name = directory + self.name + '_' + str(trial)

        if save_plot:
            LM.plot_lm_ratio(
                save_name=file_name, 
                save_plot=True, show_plot=False)

        if save_data:
            LM.save_data_and_params(file_name)

        del LM

    def properties_changed(self):
        """The properties 'Apply' button was clicked: updating image"""
        self.name = self.properties.dataset.name
        self.age = self.properties.dataset.age
        self.peakL = self.properties.dataset.lpeak
        self.peakM = self.properties.dataset.mpeak
        self.ref_LED = self.properties.dataset.data0
        self.LED1 = self.properties.dataset.data1
        self.LED2 = self.properties.dataset.data2
        self.LED3 = self.properties.dataset.data3      
        self.show_data()

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setup()
        
    def setup(self):
        """Setup window parameters"""
        self.setWindowIcon(get_icon('python.png'))
        self.setWindowTitle('LM cone ratios')
        self.resize(QSize(400, 600))

        # File menu
        file_menu = self.menuBar().addMenu(("File"))
        quit_action = create_action(self, ("Quit"),
                shortcut="Ctrl+Q",
                icon=get_std_icon("DialogCloseButton"),
                tip=("Quit application"),
                triggered=self.close)
        add_actions(file_menu, (quit_action,))

        help_menu = self.menuBar().addMenu("Edit")
        change_OD_action = create_action(self, ("Parameters"),
                 triggered=self.change_OD)
        add_actions(help_menu, (change_OD_action,))
        

        # Set central widget:
        self.mainwidget = CentralWidget(self)
        self.setCentralWidget(self.mainwidget)

    def change_OD(self):
        """Change the OD assumed in the equations"""
        pass
        
if __name__ == '__main__':
    from guidata import qapplication
    app = qapplication()
    window = MainWindow()
    window.show()
    app.exec_()
