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

# array of the name of the selected regions, set to None for the World
regions = ['Italy']


# connection parameters_________________________________________________________

proxy = {'https_proxy': 'proxy.onera:80'}




################################################################################
# Data
#
# raw data______________________________________________________________________

rawdata = rd.RawData(git_env=proxy, **raw_data)


# get time-series_______________________________________________________________

# time
time = rawdata.get_time()

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




################################################################################
# Plot
#
# initialize figure_____________________________________________________________

fig = plt.figure()
ax  = plt.subplot(111)


# plot histograms_______________________________________________________________

ax.bar(time,  active   , color=[1., .8, 0.], label=r'active cases')
ax.bar(time, -deaths   , color=[1., 0., 0.], label=r'deaths')
ax.bar(time, -recovered, color=[0., 0., 1.], label=r'recovered', bottom=-deaths)


# plot new cases________________________________________________________________

ax.plot(time, new, '-k', label=r'new cases')


# plot peak_____________________________________________________________________

# active cases
iM = np.argmax(active)
ax.plot(time[iM], active[iM], '+k', label='maxima')
ax.text(time[iM], active[iM], r'$%d~$' %(active[iM]),
        va='bottom', ha='right')

# new cases
iM = np.argmax(new)
ax.plot(time[iM], new[iM], '+k')
ax.text(time[iM], new[iM], r'$%d~$' %(new[iM]),
        va='bottom', ha='right')


# plot last data-point__________________________________________________________

# active cases
ax.plot(time[-1], active[-1], '.k', label='last point')
ax.text(time[-1], active[-1], r'$~%d$' %(active[-1]),
        va='bottom', ha='left')

# new cases
ax.plot(time[-1], new[-1], '.k')
ax.text(time[-1], new[-1], r'$~%d$' %(new[-1]),
        va='bottom', ha='left')

# deaths
ax.plot(time[-1], -deaths[-1], '.k')
ax.text(time[-1], -deaths[-1], r'$~%d$' %(deaths[-1]),
        va='top', ha='left')

# recovered
ax.plot(time[-1], -recovered[-1]-deaths[-1], '.k')
ax.text(time[-1], -recovered[-1]-deaths[-1], r'$~%d$' %(recovered[-1]),
        va='top', ha='left')


# axes__________________________________________________________________________

# axis limits
ax.set_xlim([np.min(time)-dt.timedelta(days=1), np.max(time)+dt.timedelta(days=1)])
ax.set_ylim(np.array([-1, 1])*np.max(np.abs(ax.get_ylim())))

# position (to fit the date)
bb = ax.get_position()
bb.y0+= (1-bb.y1)/3.; bb.y1+= (1-bb.y1)/3.; 
ax.set_position(bb)

# grid
ax.plot(ax.get_xlim(), [0., 0.], '-k', lw=.8)
ax.grid('minor')

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
	ax.text(0., 1., r'$\times 10^{%d}$' %(scale), transform=ax.transAxes)
# - fix ticks and compute labels
tks = [np.round(tk/(10**scale))*(10**scale) for tk in tks]
ax.set_yticks(tks)
ax.set_yticklabels(['%d' %(np.abs(tk)/(10**scale)) for tk in tks])

# labels and title
ax.set_ylabel(r'inactive $\quad|\quad$ $~$active$~$')

# title
if isinstance(regions, list): title = ' + '.join(regions)
else: title = 'World'
ax.set_title('%s (total = %d)' %(title, confirmed[-1]))

# legend
ax.legend(framealpha=1., loc='lower left')


# save figure___________________________________________________________________

if not(os.path.isdir('figs')): os.mkdir('figs')
fig.savefig(os.path.join('figs', 'istogram.pdf'))
