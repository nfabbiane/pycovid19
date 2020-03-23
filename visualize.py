##############################################################################80
#                                                                              #
#                              COVID-19 STATISTICS                             #
#                                                                              #
# (2020) Nicolo Fabbiane                                                       #
#                                                                              #
################################################################################

# system
import os, sys

# math 
import numpy as np
from scipy import optimize as spo
import datetime as dt

# visualization
from matplotlib import rc
from matplotlib import pyplot as plt
from matplotlib import patches as ptc

# local libraries
import libpy.rawdata as rd




################################################################################
# Parameters
#
# data_set file_________________________________________________________________

if len(sys.argv) > 1: data_set = os.path.basename(sys.argv[1]).split('.')[0]
else: data_set = 'jhu'

# load data_set data
ds = __import__(data_set)


# common________________________________________________________________________

# number of days in the future
future = 7




################################################################################
# Data
#
# raw data______________________________________________________________________

rawdata = rd.RawData(**ds.raw_data)




################################################################################
# Loop on figures
#
# initialize figure_____________________________________________________________

# force text to sans-serif
rc('font', family='sans-serif')
rc('text.latex', preamble=[r'\usepackage{cmbright}', r'\usepackage{amsmath}'])
rc('text', usetex=True)

# create figure and axes
fig = plt.figure()
ax  = plt.subplot(111)

# axes position (to fit the date)
bb = ax.get_position()
bb.y0+= (1-bb.y1)/3.; bb.y1+= (1-bb.y1)/3.;
bb.x1-=    bb.x0 /1.5;bb.x0-=    bb.x0 /4.;
ax.set_position(bb)

# create twin ax for final values as ticks
axt = ax.twinx()
axt.set_position(ax.get_position())


# loop__________________________________________________________________________

for title, regions in ds.figures.items():

	# get time-series___________________________________________________________

	# time
	time = np.array(rawdata.get_time())
	
	print('')
	print('%s: %s' %(title, time[-1]))

	# cumulative data for the requested regions
	confirmed, recovered, deaths, active, intensive = rawdata.get_data_for_regions(regions)

	# transform in numpy arrays
	confirmed = np.array(confirmed)
	recovered = np.array(recovered)
	deaths    = np.array(deaths)
	active    = np.array(active)
	intensive = np.array(intensive)

	# compute new daily cases
	new   = np.append([0], confirmed[1:]-confirmed[:-1])

	# compute  daily delta
	Dday_confirmed = (confirmed[-1]-confirmed[-2])/float(confirmed[-2])
	Dday_active    = (active[-1]   -active[-2]   )/float(active[-2])
	Dday_deaths    = (deaths[-1]   -deaths[-2]   )/float(deaths[-2])
	Dday_recovered = (recovered[-1]-recovered[-2])/float(recovered[-2])
	Dday_intensive = (intensive[-1]-intensive[-2])/float(intensive[-2])


	# compute logistic fit______________________________________________________

	days = np.array([(t-time[-1]).days for t in time])

	# define sigmoid function
	def sigmoid(x, A, a, b):
		return A/(1. + np.exp((b-x)/a))

	# define sigmoid function
	def dsigmoiddx(x, A, a, b):
		return A/(1. + np.exp((b-x)/a))**2 * np.exp((b-x)/a) / a

	# define sigmoid function
	def fitfun(x, C, ac, bc, D, ad, bd, R, ar, br):
		R = C-D
		return [[sigmoid(xi, C, ac, bc),
		         sigmoid(xi, D, ad, bd),
		         sigmoid(xi, R, ar, br)] for xi in x]

	# define error function
	def fiterr(ps, Xs, Ys):
		ys = fitfun(Xs, *ps)
		error = np.sum((np.array(Ys) - np.array(ys))**2)
		return error

	# comupte coefficients
	Ys = [[c, d, r] for c, d, r in zip(confirmed, deaths, recovered)]
	p0 =  (2*confirmed[-1], 1., future,
	       2*   deaths[-1], 1., future,
	       2*recovered[-1], 1., future)
	bd = ((confirmed[-1], np.inf), ( 1., np.inf), (-np.inf, np.inf),
	      (   deaths[-1], np.inf), ( 1., np.inf), (-np.inf, np.inf),
	      (recovered[-1], np.inf), ( 1., np.inf), (-np.inf, np.inf))
	sol = spo.minimize(fiterr, args=(days, Ys), x0=p0, bounds=bd)
	confirmed_psig= sol.x[0:3]
	deaths_psig   = sol.x[3:6]
	recovered_psig= sol.x[6:9]; recovered_psig[0]=confirmed_psig[0]-deaths_psig[0]
	print('           |      today      |    tomorrow     | final  ')
	print('-----------+-----------------+-----------------+--------')
	print(' confirmed | %6d (%+6d) | %6d (%+6d) | %6d'
	      %(confirmed[-1], confirmed[-1]-confirmed[-2],
	        int(sigmoid(1, *confirmed_psig)), int(dsigmoiddx(1, *confirmed_psig)),
	        int(confirmed_psig[0])))
	print(' deaths    | %6d (%+6d) | %6d (%+6d) | %6d'
	      %(deaths[-1], deaths[-1]-deaths[-2],
	        int(sigmoid(1, *deaths_psig)), int(dsigmoiddx(1, *deaths_psig)),
	        int(deaths_psig[0])))
	print(' recovered | %6d (%+6d) | %6d (%+6d) | %6d'
	      %(recovered[-1], recovered[-1]-recovered[-2],
	        int(sigmoid(1, *recovered_psig)), int(dsigmoiddx(1, *recovered_psig)),
	        int(recovered_psig[0])))


	# re-initialize figure______________________________________________________

	ax.cla()


	# plot histograms___________________________________________________________

	hh = [] # collect handles for legend
	hh.append(ax.bar(time,  active   , color=[1., .8, 0.], label=r'total active cases'))
	hh.append(ax.bar(time,  intensive, color=[1., .5, 0.], label=r'intensive-care'))
	hh.append(ax.bar(time, -deaths   , color=[1., 0., 0.], label=r'deaths'))
	hh.append(ax.bar(time, -recovered, color=[0., 0., 1.], bottom=-deaths, label=r'recovered'))
	
	# add projection to legend
	hh.append(ptc.Patch(color='none', label=r'$%+.1f\%%$/day' %(Dday_active*100)))
	hh.append(ptc.Patch(color='none', label=r'$%+.1f\%%$/day' %(Dday_intensive*100)))
	hh.append(ptc.Patch(color='none', label=r'$%+.1f\%%$/day' %(Dday_deaths*100)))
	hh.append(ptc.Patch(color='none', label=r'$%+.1f\%%$/day' %(Dday_recovered*100)))


	# plot new cases____________________________________________________________

	hl = [] # collect handles for legend
	hl+= ax.plot(time, new, '-k', label=r'new cases')


	# exponential fits__________________________________________________________
	
	# compute x0
	past = confirmed_psig[2] - confirmed_psig[1]*np.log(confirmed_psig[0]/1.-1.)
	past = int(np.max([past, np.min(days)]))

	# extend time
	dayse = np.array(range(past, int(future)+1))
	timee = np.array([time[-1] + dt.timedelta(days=d) for d in dayse])

	# plot projections - sigmoid
	ax.plot(timee, -sigmoid(dayse, *deaths_psig)-sigmoid(dayse, *recovered_psig), '--', color=[0., 0., 1.], lw=.8)
	ax.plot(timee, -sigmoid(dayse, *deaths_psig)                                , '--', color=[1., 0., 0.], lw=.8)
	ax.plot(timee, -sigmoid(dayse, *deaths_psig)-sigmoid(dayse, *recovered_psig)
	               +sigmoid(dayse, *confirmed_psig)                             , '--', color=[1., .8, 0.], lw=.8)
	hl+= ax.plot(timee,  dsigmoiddx(dayse, *confirmed_psig), '--', color=[0., 0., 0.], lw=.8, label=r'logistic fit')


	# plot peak_________________________________________________________________

	# active cases
	iM = np.argmax(active)
	hl+= ax.plot(time[iM], active[iM], '.k', label='maxima')
	ax.text(time[iM], active[iM], r'$~%d~$' %(active[iM]), va='bottom', ha='left')

	# intensive-care cases
	iM = np.argmax(intensive)
	ax.plot(time[iM], intensive[iM], '.k')
	ax.text(time[iM], intensive[iM], r'$~%d~$' %(intensive[iM]), va='top', ha='left')

	# new cases
	iM = np.argmax(new)
	ax.plot(time[iM], new[iM], '.k')
	ax.text(time[iM], new[iM], r'$~%d~$' %(new[iM]), va='bottom', ha='left')


	# plot last data-point______________________________________________________

	# initialize final point ticks and labels
	tks = []; lbl = []

	# active cases
	tks.append(active[-1])
	lbl.append(r'$%d~(%.1f\%%)$' %(active[-1], active[-1]/float(confirmed[-1])*100))

	# new cases
	tks.append(new[-1])
	lbl.append(r'$%d~(%.1f\%%)$' %(new[-1], new[-1]/float(confirmed[-1])*100))

	# intensive-care cases
	#tks.append(intensive[-1])
	#lbl.append(r'$%d~(%.1f\%%\mbox{~actives})$' %(intensive[-1], intensive[-1]/float(active[-1])*100))

	# deaths
	tks.append(-deaths[-1])
	lbl.append(r'$%d~(%.1f\%%)$' %(deaths[-1], deaths[-1]/float(confirmed[-1])*100))

	# recovered
	tks.append(-recovered[-1]-deaths[-1])
	lbl.append(r'$%d~(%.1f\%%)$' %(recovered[-1], recovered[-1]/float(confirmed[-1])*100))

	# add values and labels as tick of secondary axis
	axt.set_yticks(tks)
	axt.set_yticklabels(lbl)


	# axes______________________________________________________________________

	# axis limits
	ax.set_xlim([np.max(time)+dt.timedelta(days=past), np.max(time)+dt.timedelta(days=future)])
	ax.set_ylim(np.array([-1, 1])*confirmed_psig[0])
	
	# grid
	ax.plot(ax.get_xlim(), [0., 0.], '-k', lw=.8)
	ax.grid()

	# x ticks
	tks = [np.max(time)+dt.timedelta(days=future)]
	while tks[-1] >= np.max(time)+dt.timedelta(days=past):
		tks+= [tks[-1]-dt.timedelta(days=7)]
	tks.pop(-1)
	# - fix ticks and compute labels
	ax.set_xticks(tks)
	ax.set_xticklabels([tk.date() for tk in tks], rotation=30, ha='right')

	# y ticks
	tks = ax.get_yticks()
	# - compute scale (avoid thousands)
	scale =  int(np.floor(np.log10(np.max(tks))/3))*3
	if scale != 0:
		ax.text(0., 1.01, r'$\times 10^{%d}$' %(scale), transform=ax.transAxes)
	# - fix ticks and compute labels
	tks = [np.round(tk/(10**scale))*(10**scale) for tk in tks]
	ax.set_yticks(tks)
	ax.set_yticklabels(['%d' %(np.abs(tk)/(10**scale)) for tk in tks])

	# labels and title
	ax.set_ylabel('inactive~$\quad|\quad$~~active~\mbox{}')

	# title
	ax.set_title('%s -- $%d$ confirmed cases' %(title, confirmed[-1]))

	# legend(s)
	l1 = ax.legend(hh, [h.get_label() for h in hh], framealpha=1., loc='lower left', ncol=2)
	l2 = ax.legend(hl, [h.get_label() for h in hl], framealpha=1., loc='upper left', ncol=1)
	ax.add_artist(l1)

	# axis limits (secondary axis)
	ax.set_ylim(np.array([-1, 1])*confirmed_psig[0])
	axt.set_ylim(ax.get_ylim())


	# save figure_______________________________________________________________

	if not(os.path.isdir('figs')): os.mkdir('figs')
	fig.savefig(os.path.join('figs', 'histogram_%s.pdf' %(title)))
	fig.savefig(os.path.join('figs', 'histogram_%s.png' %(title)))
