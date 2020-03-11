##############################################################################80
#                                                                              #
#                              COVID-19 STATISTICS                             #
#                                                                              #
# (2020) Nicolo Fabbiane                                                       #
#                                                                              #
################################################################################

# system
import os, sys
import importlib

# math 
import numpy as np
import datetime as dt

# visualization
from matplotlib import rc
from matplotlib import pyplot as plt

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

# number of points considered for exponential projection
nexp = 4




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

	# cumulative data for the requested regions
	confirmed, recovered, deaths, active, intensive = rawdata.get_data_for_regions(regions)

	# transform in numpy arrays
	confirmed = np.array(confirmed)
	recovered = np.array(recovered)
	deaths    = np.array(deaths)
	active    = np.array(active)
	intensive = np.array(intensive)

	# compute new daily cases
	dtime = (time[1:]-time[:-1])
	timen = np.array([t + td/2. for t, td in zip(time[:-1], dtime)])
	new   = confirmed[1:]-confirmed[:-1]


	# compute exponential fit___________________________________________________

	days = np.array([(t-time[-1]).days for t in time])

	# comupte coefficients
	active_coefs    = np.polyfit(days[-nexp:], np.log(active[-nexp:]), 1)
	deaths_coefs    = np.polyfit(days[-nexp:], np.log(deaths[-nexp:]), 1)
	recovered_coefs = np.polyfit(days[-nexp:], np.log(recovered[-nexp:]), 1)
	intensive_coefs = np.polyfit(days[-nexp:], np.log(intensive[-nexp:]), 1)

	# compute doubling time
	time2_active    = np.log(2.)/active_coefs[0]
	time2_deaths    = np.log(2.)/deaths_coefs[0]
	time2_recovered = np.log(2.)/recovered_coefs[0]
	time2_intensive = np.log(2.)/intensive_coefs[0]


	# re-initialize figure______________________________________________________

	ax.cla()


	# plot histograms___________________________________________________________

	hh = [] # collect handles for legend
	hh.append(ax.bar(time,  active   , color=[1., .8, 0.],
	          label=r'total active cases ($\times 2$ in $%.1f$ days)' %(time2_active)))
	hh.append(ax.bar(time,  intensive, color=[1., .5, 0.],
	          label=r'intensive-care ($\times 2$ in $%.1f$ days)' %(time2_intensive)))
	hh.append(ax.bar(time, -deaths   , color=[1., 0., 0.],
	          label=r'deaths ($\times 2$ in $%.1f$ days)' %(time2_deaths)))
	hh.append(ax.bar(time, -recovered, color=[0., 0., 1.], bottom=-deaths,
	          label=r'recovered ($\times 2$ in $%.1f$ days)' %(time2_recovered)))


	# plot new cases____________________________________________________________

	hl = [] # collect handles for legend
	hl+= ax.plot(timen, new, '-k', label=r'new cases')


	# exponential fits__________________________________________________________

	# extend time
	timee = np.append(time[-nexp:], time[-1] + dt.timedelta(days=1))
	dayse = np.append(days[-nexp:], 1)

	# plot projections
	hl+= ax.plot(timee, np.exp(active_coefs[1]+active_coefs[0]   *dayse), '--k', zorder=0, label=r'exp. fit')
	ax.plot(timee, np.exp(intensive_coefs[1] + intensive_coefs[0]*dayse), '--k', zorder=0)
	ax.plot(timee,-np.exp(deaths_coefs[1]    + deaths_coefs[0]   *dayse), '--k', zorder=0)
	ax.plot(timee,-np.exp(deaths_coefs[1]    + deaths_coefs[0]   *dayse)
				  -np.exp(recovered_coefs[1] + recovered_coefs[0]*dayse), '--k', zorder=0)


	# plot peak_________________________________________________________________

	# active cases
	iM = np.argmax(active)
	hl+= ax.plot(time[iM], active[iM], '.k', label='maxima')
	ax.text(time[iM], active[iM], r'$%d~$' %(active[iM]), va='bottom', ha='center')

	# intensive-care cases
	iM = np.argmax(intensive)
	ax.plot(time[iM], intensive[iM], '.k')
	ax.text(time[iM], intensive[iM], r'$%d~$' %(intensive[iM]), va='bottom', ha='center')

	# new cases
	iM = np.argmax(new)
	ax.plot(timen[iM], new[iM], '.k')
	ax.text(timen[iM], new[iM], r'$%d~$' %(new[iM]), va='bottom', ha='center')


	# plot last data-point______________________________________________________

	# initialize final point ticks and labels
	tks = []; lbl = []

	# active cases
	tks.append(active[-1])
	lbl.append(r'$%d~(%.1f\%%)$' %(active[-1], active[-1]/float(confirmed[-1])*100))

	# intensive-care cases
	tks.append(intensive[-1])
	lbl.append(r'$%d~(%.1f\%%)$' %(intensive[-1], intensive[-1]/float(confirmed[-1])*100))

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
	ax.set_xlim([np.min(time)-dt.timedelta(days=1), np.max(time)+dt.timedelta(days=1)])
	ax.set_ylim(np.array([-1, 1])*np.max(np.abs(ax.get_ylim())))

	# grid
	ax.plot(ax.get_xlim(), [0., 0.], '-k', lw=.8)
	ax.grid()

	# x ticks
	tks = [np.max(time)]
	while tks[-1] >= np.min(time): tks+= [tks[-1]-dt.timedelta(days=7)]
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
	ax.set_title('%s: $%d$ confirmed cases ($%+.1f\%%$)' %(title, confirmed[-1], new[-1]/confirmed[-2]*100))

	# legend(s)
	l1 = ax.legend(hh, [h.get_label() for h in hh], framealpha=1., loc='lower left')
	l2 = ax.legend(hl, [h.get_label() for h in hl], framealpha=1., loc='upper left', ncol=len(hl))
	ax.add_artist(l1)

	# axis limits (secondary axis)
	axt.set_ylim(ax.get_ylim())


	# save figure_______________________________________________________________

	if not(os.path.isdir('figs')): os.mkdir('figs')
	fig.savefig(os.path.join('figs', 'histogram_%s.pdf' %(title)))
	fig.savefig(os.path.join('figs', 'histogram_%s.png' %(title)))
