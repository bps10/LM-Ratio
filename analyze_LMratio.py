from __future__ import division
import numpy as np
import matplotlib.pylab as plt
from scipy.optimize import minimize

from base import plot as pf
from base import spectsens as spect
from base import optics as o

class LMratio():
	'''
	ToDo
	=====
	1. report error in estimate
	'''

	def __init__(self, LED_path='LEDspectra.csv'):
		'''
		'''
		self.cones = {}
		self.cones['L_OD'] = 0.35
		self.cones['M_OD'] = 0.22

		self.import_LED(LED_path)
		
	def set_parameters(self, age=26, L_peak=559, M_peak=530):
		'''
		'''
		self.age = age

		self.cones['L_peak'] = L_peak
		self.cones['M_peak'] = M_peak

		self.get_lens()
		self.get_cones()
		self.set_LED_ratios()

	def set_LED_rel_intensities(self, ref, light1, light2, light3):
		'''
		'''
		d = {}
		d['ref'] = np.mean(np.asarray(ref))
		d[1] = np.mean(np.asarray(light1))
		d[2] = np.mean(np.asarray(light2))
		d[3] = np.mean(np.asarray(light3))

		self.data = {}
		self.data['raw_ref'] = np.mean(np.asarray(ref))
		self.data['raw_1'] = np.mean(np.asarray(light1))
		self.data['raw_2'] = np.mean(np.asarray(light2))
		self.data['raw_3'] = np.mean(np.asarray(light3))

		self.data['STDref'] = np.std(np.asarray(ref))
		self.data['STD1'] = np.std(np.asarray(light1))
		self.data['STD2'] = np.std(np.asarray(light2))
		self.data['STD3'] = np.std(np.asarray(light3))

		self.data['ref'] = _correct(d['ref'], d['ref'], 1)
		self.data[1] = _correct(d['ref'], d[1], self.led_ratio[1])
		self.data[2] = _correct(d['ref'], d[2], self.led_ratio[2])
		self.data[3] = _correct(d['ref'], d[3], self.led_ratio[3])
		self.data['LED_peaks'] = self.LED['LED_peaks']

	def get_lens(self):
		'''
		'''
		self.lens = (10 ** o.lens_age_correction(self.age, 
			self.spectrum)) ** -1

	def import_LED(self, path):
		'''
		'''
		names = ['wavelength', 'ref', '1', '2', '3']

		led = np.genfromtxt(path, 
			delimiter=',', skip_header=2, names=names)
		self.spectrum = led['wavelength']

		self.LED = {}
		for name in names:
			self.LED[name] = led[name]

		self.LED['p0'] = self.spectrum[np.argmax(led['ref'])]
		self.LED['p1'] = self.spectrum[np.argmax(led['1'])]
		self.LED['p2'] = self.spectrum[np.argmax(led['2'])]
		self.LED['p3'] = self.spectrum[np.argmax(led['3'])]
		self.LED['LED_peaks'] = np.array([
			self.LED['p0'], self.LED['p1'], self.LED['p2'],
			self.LED['p3']])
		self.LED['ind0'] = np.argmax(led['ref'])
		self.LED['ind1'] = np.argmax(led['1'])
		self.LED['ind2'] = np.argmax(led['2'])
		self.LED['ind3'] = np.argmax(led['3'])

		_r = {};
		_r[1] = self.LED['ref'].sum() / self.LED['1'].sum()
		_r[2] = self.LED['ref'].sum() / self.LED['2'].sum()
		_r[3] = self.LED['ref'].sum() / self.LED['3'].sum()
		self.led_ratio = _r

	def get_cones(self):
		'''
		'''
		L_cones = spect.neitz(LambdaMax=self.cones['L_peak'], 
			OpticalDensity=self.cones['L_OD'], 
			LOG=False, StartWavelength=self.spectrum[0], 
			EndWavelength=self.spectrum[-1], 
            resolution=1, EXTINCTION=False)
		M_cones = spect.neitz(LambdaMax=self.cones['M_peak'], 
			OpticalDensity=self.cones['M_OD'], 
			LOG=False, StartWavelength=self.spectrum[0], 
			EndWavelength=self.spectrum[-1], 
			resolution=1, EXTINCTION=False)

		M = M_cones * self.lens
		self.cones['M'] = M / M.max()
		L = L_cones * self.lens
		self.cones['L'] = L / L.max()

	def find_LMratio(self, RETURN=True, PRINT=True, correct=False):
		'''
		'''
		self.l_frac = self.solve_LM_ratio()
		self.l_frac_error = np.sqrt(self._solve_fun(
			self.l_frac).sum())
		
		lm_ratio = self.l_frac / (1 - self.l_frac)

		if correct:	
			self.l_frac = self._correct_lm_ratio()

		if PRINT:
			print self.l_frac_error
			print 'L:M ' + str(round(lm_ratio, 3))
			print 'L/(L+M) ' + str(round(self.l_frac, 3))	

		if RETURN:
			return self.l_frac, self.l_frac_error

	def _correct_lm_ratio(self, factor=1.5):
		'''
		'''
		lm_ratio = self.l_frac / (1 - self.l_frac)
		# correction factor from Hofer et al. 2005
		lm_ratio *= factor 
		return lm_ratio / (1 + lm_ratio)

	def gen_LM_fit(self):
		'''
		'''
		self.fit = LM_fit(self.cones['L'], self.cones['M'], 
			self.l_frac)
		self.fit = self.fit / np.max(self.fit)

	def solve_LM_ratio(self):
		'''
		'''
		# error function to minimize
		err = lambda l_const: (self._solve_fun(l_const)).sum()
		w = minimize(err, 0.5)

		return w.x # the solution

	def set_LED_ratios(self):
		'''
		'''
		r = {}
		r[1] = self.LED['ref'].sum() / self.LED['1'].sum()
		r[2] = self.LED['ref'].sum() / self.LED['2'].sum()
		r[3] = self.LED['ref'].sum() / self.LED['3'].sum()
		self.led_ratio = r

	def _solve_fun(self, l):
		'''
		'''
		curve = LM_fit(self.cones['L'], self.cones['M'], l)
		curve = curve / curve.max()

		norm = self.diff_sens(curve)

		data1 = self.data[1] / norm
		data2 = self.data[2] / norm
		data3 = self.data[3] / norm

		light1 = curve[self.LED['ind1']]
		light2 = curve[self.LED['ind2']]
		light3 = curve[self.LED['ind3']]

		rms = (light1 - data1) ** 2 + (light2 - data2) ** 2 + (
			light3 - data3) ** 2

		return rms

	def diff_sens(self, curve):
		'''
		'''
		# maximum possible
		fake_cone = spect.neitz(
			LambdaMax=self.spectrum[self.LED['ind0']], 
			OpticalDensity=0.3, 
			LOG=False, 
			StartWavelength=self.spectrum[0], 
			EndWavelength=self.spectrum[-1], 
            resolution=1, EXTINCTION=False)

		norm = (np.sum(fake_cone * self.LED['ref']) / 
			np.sum(curve * self.LED['ref']))

		return norm

	def plot_lm_ratio(self, save_name='lm ratio', save_plot=False,
		show_plot=True):
		'''
		'''
		self.gen_LM_fit()

		fig1 = plt.figure(figsize=(6.5, 6.5))
		fig1.set_tight_layout(True)	
		ax = fig1.add_subplot(111)
		pf.AxisFormat(ticksize=19, fontsize=30)
		pf.TufteAxis(ax, ['left', 'bottom'], [4, 4])

		ax.plot(self.spectrum, np.log10(self.cones['M']), 'g--')
		ax.plot(self.spectrum, np.log10(self.cones['L']), 'r--')
		ax.plot(self.spectrum, np.log10(self.fit), 'k')

		norm = self.diff_sens(self.fit)

		ax.plot(self.LED['p0'], np.log10(self.data['ref'] / norm), '^', 
			markersize=12, color='k')

		ax.errorbar(self.LED['p1'], np.log10(self.data[1] / norm), 
			fmt='o', yerr=self.data['STD1'], markersize=12, color='k')
		ax.errorbar(self.LED['p2'], np.log10(self.data[2] / norm), 
			fmt='o', yerr=self.data['STD2'], markersize=12, color='k')
		ax.errorbar(self.LED['p3'], np.log10(self.data[3] / norm), 
			fmt='o', yerr=self.data['STD3'], markersize=12, color='k') 
		
		ax.set_xlim([440, 700])
		ax.set_ylim([-2, np.max(np.log10(self.cones['L'])) + 0.01])
		ax.set_ylabel('rel. sensitivity')
		ax.set_xlabel('wavelength (nm)')
		
		if save_plot:
			plt.savefig(save_name + '.png')
			plt.savefig(save_name + '.eps')

		if show_plot:
			plt.show()
	
	def plot_spectrum_cones(self):

		fig = plt.figure(figsize=(7, 8))
		fig.set_tight_layout(True)
		ax1 = fig.add_subplot(211)
		ax2 = fig.add_subplot(212)
		
		pf.AxisFormat(ticksize=19, fontsize=30)
		pf.TufteAxis(ax1, ['left', ], [3, 3])
		pf.TufteAxis(ax2, ['left', 'bottom'], [3, 3])
		
		ax1.plot(self.spectrum, self.LED['ref'], 'k-')
		ax1.plot(self.spectrum, self.LED['1'], 'k--')
		ax1.plot(self.spectrum, self.LED['2'], 'k-.')
		ax1.plot(self.spectrum, self.LED['3'], 'k.')
		ax2.plot(self.spectrum, self.lens, 'k')
		ax2.plot(self.spectrum, self.cones['L'], 'r')
		ax2.plot(self.spectrum, self.cones['M'], 'g')

		ax1.set_xlim([400, 700])
		ax2.set_xlim([400, 700])
		plt.show()

	def save_data_and_params(self, save_name='LM ratio'):
		'''
		'''
		data = {}
		self.gen_LM_fit()
		norm = self.diff_sens(self.fit)
		data['ref'] = self.data['raw_ref']
		data['LED1'] = self.data['raw_1']
		data['LED2'] = self.data['raw_2']
		data['LED3'] = self.data['raw_3']

		data['L_perc'] = self.l_frac[0] * 100
		data['M_perc'] = 100 - data['L_perc']
		data['L_corr'] = self._correct_lm_ratio()[0] * 100
		data['M_corr'] = 100 - data['L_corr']
		data['lm_error'] = self.l_frac_error * 100

		data['L_peak'] = str(self.cones['L_peak'])
		data['M_peak'] = str(self.cones['M_peak'])
		data['age'] = self.age

		txt = ''
		for key in data:
			txt += key + ',' + str(data[key]) + '\n'
		fil = open(save_name + '.csv', 'w')
		fil.write(txt)
		fil.close()

	def return_fit(self):
		'''
		'''
		self.gen_LM_fit()
		return self.fit

	def return_spectrum(self):
		'''
		'''
		return self.spectrum

	def return_cones(self):
		'''
		'''
		return self.cones

	def return_data(self):
		'''
		'''
		self.gen_LM_fit()
		norm = self.diff_sens(self.fit)
		self.data['ref'] = self.data['ref'] / norm
		self.data[1] = self.data[1] / norm
		self.data[2] = self.data[2] / norm
		self.data[3] = self.data[3] / norm
		return self.data

def LM_fit(L, M, l_frac):
	'''
	'''
	return (1 - l_frac) * M + l_frac * L


def _correct(ref, test_int, led_ratio):
	'''
	'''
	return (ref / test_int) * led_ratio


def plot_ERG_trace_schematic():
	'''
	'''
	fig = plt.figure()
	fig.set_tight_layout(True)
	ax = fig.add_subplot(111)
	pf.AxisFormat()
	pf.TufteAxis(ax, ['left', 'botton'], [5, 5])	
	x = np.linspace(0, 2 * np.pi, 200)
	ax.plot(x, np.sin(x), 'k')
	ax.plot(x, 0.5 * np.sin(x), 'k')
	ax.plot(x, 0.1 * np.sin(x), 'k')
	ax.plot(x, 0.01 * np.sin(x), 'k')
	plt.show()


if __name__ == '__main__':

	LM = LMratio()
	### Default is JN's parameters
	LM.set_parameters(age=54, L_peak=559, M_peak=530)
	LM.set_LED_rel_intensities(ref=10, light1=18.5, 
		light2=9.875, light3=27.333)
	LM.find_LMratio()
	#LM.plot_spectrum_cones()
	LM.plot_lm_ratio()
	LM.save_data_and_params()
