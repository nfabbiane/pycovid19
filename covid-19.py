##############################################################################80
#                                                                              #
#                              COVID-19 STATISTICS                             #
#                                                                              #
# (2020) Nicolo Fabbiane                                                       #
#                                                                              #
################################################################################

# system
import os

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
# data origin___________________________________________________________________

# John Hopkins University
raw_data = {'path'   : 'data/JHU',
            'git_url': 'https://github.com/CSSEGISandData/COVID-19.git'}


# plot__________________________________________________________________________

# dictionary of figures: the key is the figure name, while the value is the
# list of names of the selected regions. Set it to None for the World.
figures = {'Italy' : ['Italy'],
           'France': ['France'],
           'EU'    : ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 
                      'Czech Republic', 'Denmark', 'Estonia', 'Finland',
                      'France', 'Germany', 'Greece', 'Hungary', 'Ireland',
                      'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta',
                      'Netherlands', 'Poland', 'Portugal', 'Romania',
                      'Slovakia', 'Slovenia', 'Spain', 'Sweden'],
           'World' : None }

# number of points considered for exponential projection
nexp = 4




################################################################################
# Data
#
# raw data______________________________________________________________________

rawdata = rd.RawData(**raw_data)




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


# loop__________________________________________________________________________

for title, regions in figures.items():

	# get time-series___________________________________________________________

	# time
	time = np.array(rawdata.get_time())

	# cumulative data for the requested regions
	confirmed, recovered, deaths = rawdata.get_data_for_regions(regions)

	# transform in numpy arrays
	confirmed = np.array(confirmed)
	recovered = np.array(recovered)
	deaths    = np.array(deaths)

	# compute active cases
	active = confirmed - recovered - deaths

	# compute new daily cases
	new = np.array([0] + (confirmed[1:]-confirmed[:-1]).tolist())


	# compute exponential fit___________________________________________________

	dtime = np.array([(t-time[-1]).days for t in time])

	# comupte coefficients
	active_coefs    = np.polyfit(dtime[-nexp:], np.log(active[-nexp:]), 1)
	deaths_coefs    = np.polyfit(dtime[-nexp:], np.log(deaths[-nexp:]), 1)
	recovered_coefs = np.polyfit(dtime[-nexp:], np.log(recovered[-nexp:]), 1)

	# compute doubling time
	time2_active    = np.log(2.)/active_coefs[0]
	time2_deaths    = np.log(2.)/deaths_coefs[0]
	time2_recovered = np.log(2.)/recovered_coefs[0]


	# re-initialize figure______________________________________________________

	ax.cla()


	# plot histograms___________________________________________________________

	hh = [] # collect handles for legend
	hh.append(ax.bar(time,  active   , color=[1., .8, 0.],
	          label=r'active cases ($\times 2$ in $%.1f$ days)' %(time2_active)))
	hh.append(ax.bar(time, -deaths   , color=[1., 0., 0.],
	          label=r'deaths ($\times 2$ in $%.1f$ days)' %(time2_deaths)))
	hh.append(ax.bar(time, -recovered, color=[0., 0., 1.], bottom=-deaths,
	          label=r'recovered ($\times 2$ in $%.1f$ days)' %(time2_recovered)))


	# plot new cases____________________________________________________________

	hl = [] # collect handles for legend
	hl+= ax.plot(time, new, '-k', label=r'new cases')


	# exponential fits__________________________________________________________

	# extend time
	timee  = np.append(time[-nexp:], time[-1] + dt.timedelta(days=1))
	dtimee = np.append(dtime[-nexp:], 1)

	# plot projections
	hl+= ax.plot(timee, np.exp(active_coefs[1]    + active_coefs[0]   *dtimee), '--k', zorder=0, label=r'exp. fit')
	ax.plot(timee,-np.exp(deaths_coefs[1]    + deaths_coefs[0]   *dtimee), '--k', zorder=0)
	ax.plot(timee,-np.exp(deaths_coefs[1]    + deaths_coefs[0]   *dtimee)
				  -np.exp(recovered_coefs[1] + recovered_coefs[0]*dtimee), '--k', zorder=0)


	# plot peak_________________________________________________________________

	# active cases
	iM = np.argmax(active)
	hl+= ax.plot(time[iM], active[iM], '+k', label='maxima')
	ax.text(time[iM], active[iM], r'$%d~$' %(active[iM]),
			va='bottom', ha='right')

	# new cases
	iM = np.argmax(new)
	ax.plot(time[iM], new[iM], '+k')
	ax.text(time[iM], new[iM], r'$%d~$' %(new[iM]),
			va='bottom', ha='right')


	# plot last data-point______________________________________________________

	# active cases
	hl+= ax.plot(time[-1], active[-1], '.k', label='last point')
	ax.text(time[-1]+dt.timedelta(days=2), active[-1],
			r'$%d~(%.1f\%%)$' %(active[-1], active[-1]/float(confirmed[-1])*100),
			va='bottom', ha='left')

	# new cases
	ax.plot(time[-1], new[-1], '.k')
	ax.text(time[-1]+dt.timedelta(days=2), new[-1],
			r'$%d~(%.1f\%%)$' %(new[-1], new[-1]/float(confirmed[-1])*100),
			va='bottom', ha='left')

	# deaths
	ax.plot(time[-1], -deaths[-1], '.k')
	ax.text(time[-1]+dt.timedelta(days=2), -deaths[-1],
			r'$%d~(%.1f\%%)$' %(deaths[-1], deaths[-1]/float(confirmed[-1])*100),
			va='top', ha='left')

	# recovered
	ax.plot(time[-1], -recovered[-1]-deaths[-1], '.k')
	ax.text(time[-1]+dt.timedelta(days=2), -recovered[-1]-deaths[-1],
			r'$%d~(%.1f\%%)$' %(recovered[-1], recovered[-1]/float(confirmed[-1])*100),
			va='top', ha='left')


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
	ax.set_xticklabels([tk for tk in tks], rotation=30, ha='right')

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
	ax.set_title('%s (total = $%d$)' %(title, confirmed[-1]))

	# legend(s)
	l1 = ax.legend(hh, [h.get_label() for h in hh], framealpha=1., loc='lower left')
	l2 = ax.legend(hl, [h.get_label() for h in hl], framealpha=1., loc='upper left', ncol=len(hl))
	ax.add_artist(l1)


	# save figure_______________________________________________________________

	if not(os.path.isdir('figs')): os.mkdir('figs')
	fig.savefig(os.path.join('figs', 'histogram_%s.pdf' %(title)))
	fig.savefig(os.path.join('figs', 'histogram_%s.png' %(title)))
