from __future__ import division
from guidata.qt.QtGui import (QSplitter, QMainWindow, 
    QListWidget, QPushButton, QFileDialog, QLineEdit, QLabel)
from guidata.qt.QtCore import QSize, Qt
from guidata.configtools import get_icon
from guidata.qthelpers import create_action, add_actions, get_std_icon

from guiqwt.plot import CurveDialog, CurveWidget
from guiqwt.builder import make

import numpy as np
import sys, os

from analyze_LMratio import LMratio
from base import spectsens as spect
from base import optics as o


class CentralWidget(QSplitter):
    def __init__(self, parent):
        QSplitter.__init__(self, parent)

        self.name = 'subject'
        self.age = 26
        self.peakL = 559
        self.peakM = 530
        self.ref_LED = 10
        self.LED1 = 15
        self.LED2 = 13.9
        self.LED3 = 40.45
        self.L_OD = 0.35
        self.M_OD = 0.22

        self.setContentsMargins(10, 10, 10, 10)
        self.setOrientation(Qt.Vertical)
        
        line1 = QSplitter()
        line1.setOrientation(Qt.Horizontal)
        line2 = QSplitter()
        line2.setOrientation(Qt.Horizontal)
        line3 = QSplitter()
        line3.setOrientation(Qt.Horizontal)
        line4 = QSplitter()
        line4.setOrientation(Qt.Horizontal)
        line5 = QSplitter()
        line5.setOrientation(Qt.Horizontal)
        line6 = QSplitter()
        line6.setOrientation(Qt.Horizontal)
        line7 = QSplitter()
        line7.setOrientation(Qt.Horizontal)
        line8 = QSplitter()
        line8.setOrientation(Qt.Horizontal)

        self.txt1 = QLineEdit(str(self.name))
        self.txt1.setMaximumWidth(100)
        self.txt2 = QLineEdit(str(self.age))
        self.txt2.setMaximumWidth(100)
        self.txt3 = QLineEdit(str(self.peakL))
        self.txt3.setMaximumWidth(100)
        self.txt4 = QLineEdit(str(self.peakM))
        self.txt4.setMaximumWidth(100)
        self.txt5 = QLineEdit(str(self.ref_LED))
        self.txt5.setMaximumWidth(100)
        self.txt6 = QLineEdit()
        self.txt6.setMaximumWidth(100)
        self.txt7 = QLineEdit()
        self.txt7.setMaximumWidth(100)
        self.txt8 = QLineEdit()
        self.txt8.setMaximumWidth(100)

        label1 = QLabel('name')
        label2 = QLabel('age')
        label3 = QLabel('peak L')
        label4 = QLabel('peak M')
        label5 = QLabel('ref LED')
        label6 = QLabel('LED1')
        label7 = QLabel('LED2')
        label8 = QLabel('LED3')

        line1.addWidget(label1)
        line2.addWidget(label2)
        line3.addWidget(label3)
        line4.addWidget(label4)
        line5.addWidget(label5)
        line6.addWidget(label6)
        line7.addWidget(label7)
        line8.addWidget(label8)

        line1.addWidget(self.txt1)
        line2.addWidget(self.txt2)
        line3.addWidget(self.txt3)
        line4.addWidget(self.txt4)
        line5.addWidget(self.txt5)
        line6.addWidget(self.txt6)
        line7.addWidget(self.txt7)
        line8.addWidget(self.txt8)

        self.load_button = QPushButton('load data')
        self.load_button.clicked.connect(self.load) 

        self.analyze_button = QPushButton('analyze')
        self.analyze_button.clicked.connect(self.analyze) 

        # add left side of the bottom panel
        left_side = QSplitter()
        left_side.setOrientation(Qt.Vertical)
        left_side.addWidget(self.load_button)
        left_side.addWidget(line1)
        left_side.addWidget(line2)
        left_side.addWidget(line3)
        left_side.addWidget(line4)
        left_side.addWidget(line5)
        left_side.addWidget(line6)
        left_side.addWidget(line7)
        left_side.addWidget(line8)
        left_side.addWidget(self.analyze_button)


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

        self.show_data(PRINT=False)    

        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        self.setHandleWidth(10)
        self.setSizes([800, 1])

    def analyze(self):
        '''
        '''
        success = self.get_input_values()
        if success:
            # analyze
            self.show_data()

    def get_input_values(self):
        '''
        '''
        # check that values in
        try:
            if len(str(self.txt1.displayText())) < 2:
                raise ValueError('No subject name')
            self.name = str(self.txt1.displayText())
            self.age = float(self.txt2.displayText())
            self.peakL = float(self.txt3.displayText())
            self.peakM = float(self.txt4.displayText())
            self.ref_LED = float(self.txt5.displayText())
            self.LED1 = float(self.txt6.displayText())
            self.LED2 = float(self.txt7.displayText())
            self.LED3 = float(self.txt8.displayText())
            return True

        except ValueError:
            message = []
            message.append('ERROR: Make sure values were entered \nproperly.')
            self.results.addItems(message) 
            return False

    def load(self):
        '''
        '''
        # Open a file finder. Load the csv file.
        name = QFileDialog.getOpenFileName()
        try:
            f = open(name, 'r')
            raw_dat = f.read()
            f.close()
            proceed = True
        except IOError:
            message = []
            message.append('Could not open file.')
            self.results.addItems(message) 
            proceed = False       

        if proceed:
            data = {}
            lines = raw_dat.split('\n')
            for line in lines:
                if line != '':
                    d = line.split(',')
                    array = []
                    for num in d[1:]:
                        if num != '':
                            array.append(num)
                    data[d[0]] = np.asarray(array, dtype=float)

            if 'name' in data:
                self.txt1.setText(str(data['name'][0]))
            else:
                self.txt1.setText('')
            if 'age' in data:
                self.txt2.setText(str(data['age'][0]))
            else:
                self.txt2.setText('')
            if 'L_peak' in data:
                self.txt3.setText(str(data['L_peak'][0]))
            else:
                self.txt3.setText('')
            if 'M_peak' in data:
                self.txt4.setText(str(data['M_peak'][0]))
            else:
                self.txt4.setText('')
            if 'ref' in data:    
                self.txt5.setText(str(data['ref'][0]))
            else:
                self.txt5.setText('')
            if 'LED1' in data:   
                self.txt6.setText(str(np.mean(data['LED1'])))
            else:
                self.txt6.setText('')
            if 'LED2' in data:
                self.txt7.setText(str(np.mean(data['LED2'])))
            else:
                self.txt7.setText('')
            if 'LED3' in data:
                self.txt8.setText(str(np.mean(data['LED3'])))
            else:
                self.txt8.setText('')


    def save(self):
        '''
        '''
        success = self.get_input_values()
        if success:
            self.show_data(save_plot=True, save_data=True, PRINT=True)
            message = []
            message.append('Success! Plot and data saved.')
            self.results.addItems(message) 
        else:
            self.show_data(save_plot=True, save_data=True, PRINT=True)
            message = []
            message.append('Check input values. Data not saved')
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

        #help_menu = self.menuBar().addMenu("Edit")
        #change_OD_action = create_action(self, ("Parameters"),
        #         triggered=self.change_OD)
        #add_actions(help_menu, (change_OD_action,))
        

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
