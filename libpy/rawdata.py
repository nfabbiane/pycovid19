##############################################################################80
#                                                                              #
#                              Raw-data Reader                                 #
#                                                                              #
# (2020) Nicolo Fabbiane                                                       #
#                                                                              #
################################################################################

class RawData:
	"""
	"""
	def __init__(self, path='data', git_url=None, git_env={}, data_fmt='jhu'):
		"""
		"""
		# store data
		self.path      = path
		self.git_url   = git_url
		self.git_env   = git_env
		self.data_fmt  = data_fmt
		self.time      = {}
		self.confirmed = {}
		self.recovered = {}
		self.deaths    = {}
		self.active    = {}
		self.intensive = {}
		# initialize
		self.update_git()
		# read data
		self.read_data()
	#___________________________________________________________________________
	#
	def update_git(self):
		"""
		"""
		# modules
		import os
		from git import Repo
		# does the repo exists?
		if os.path.isdir(self.path):
			# get repo origin
			origin = Repo(self.path).remote()
			# update (pull)
			origin.pull(env=self.git_env)
		elif not(self.git_url is None):
			# clone repo from url
			repo = Repo.clone_from(self.git_url, self.path, env=self.git_env)
	#___________________________________________________________________________
	#
	def read_data(self):
		"""
		"""
		# select reader
		if self.data_fmt is 'jhu': # John Hopkins University
			data = read_data_jhu(self)
		elif self.data_fmt is 'dpc': # Dipartimento della protezione Civile
			data = read_data_dpc(self)
		elif self.data_fmt is 'ofr': # OpenCoVid19-fr
			data = read_data_ofr(self)
		else: # default (John Hopkins University)
			data = read_data_jhu(self)
		# unpack data
		self.time      = data[0]
		self.confirmed = data[1]
		self.recovered = data[2]
		self.deaths    = data[3]
		self.active    = data[4]
		self.intensive = data[5]
	#___________________________________________________________________________
	#
	def get_time(self):
		"""
		"""
		return self.time
	#___________________________________________________________________________
	#
	def get_data_for_regions(self, regions):
		"""
		"""
		# check inputs
		if not(isinstance(regions, list)):
			regions = list(self.confirmed.keys())
			regions+= list(self.recovered.keys())
			regions+= list(self.deaths.keys())
			regions = list(set(regions))
		# initialize output
		confirmed = [0]*len(self.time)
		recovered = [0]*len(self.time)
		deaths    = [0]*len(self.time)
		active    = [0]*len(self.time)
		intensive = [0]*len(self.time)
		# loop on regions
		for region in regions:
			if region in self.confirmed.keys():
				for i, data in enumerate(self.confirmed[region]):
					confirmed[i]+= data
			else: print('WARNING! %s not found in confirmed' %(region))
			if region in self.recovered.keys():
				for i, data in enumerate(self.recovered[region]):
					recovered[i]+= data
			else: print('WARNING! %s not found in recovered' %(region))
			if region in self.deaths.keys():
				for i, data in enumerate(self.deaths[region]):
					deaths[i]+= data
			else: print('WARNING! %s not found in deaths' %(region))
			if region in self.active.keys():
				for i, data in enumerate(self.active[region]):
					active[i]+= data
			else: print('WARNING! %s not found in active' %(region))
			if region in self.intensive.keys():
				for i, data in enumerate(self.intensive[region]):
					intensive[i]+= data
			else: print('WARNING! %s not found in intensive' %(region))
		# output
		return confirmed, recovered, deaths, active, intensive
	#___________________________________________________________________________
	#




################################################################################
# Support functions
#_______________________________________________________________________________
#
def read_data_jhu(rawdata):
	"""
	"""
	# modules
	import os
	# path to time-series files
	timeseries_path = os.path.join(rawdata.path, 'csse_covid_19_data', 'csse_covid_19_time_series')
	# read confirmed cases
	timeseries_file = os.path.join(timeseries_path, 'time_series_19-covid-Confirmed.csv')
	time, confirmed = read_file_jhu(timeseries_file)
	# read recovered cases
	timeseries_file = os.path.join(timeseries_path, 'time_series_19-covid-Recovered.csv')
	time, recovered = read_file_jhu(timeseries_file)
	# read deaths
	timeseries_file = os.path.join(timeseries_path, 'time_series_19-covid-Deaths.csv')
	time, deaths = read_file_jhu(timeseries_file)
	# compute active cases (and dummy intensive care)
	active = {}; intensive = {}
	for region in confirmed.keys():
		active[region]    = [0]*len(confirmed[region])
		intensive[region] = [0]*len(confirmed[region])
		for i in range(len(confirmed[region])):
			active[region][i] = confirmed[region][i]
			active[region][i]-= recovered[region][i] + deaths[region][i]
	# output
	return time, confirmed, recovered, deaths, active, intensive
#_______________________________________________________________________________
#
def read_file_jhu(filename):
	"""
	"""
	# modules
	import datetime as dt
	# open file
	f = open(filename, 'r')
	# read header (time-stamps)
	line = f.readline().rstrip('\r\n').split(',')
	time = [dt.datetime.strptime(t, '%m/%d/%y') for t in line[4:]]
	# loop on entries
	data_by_region={}
	for l in f:
		# split line
		line = l.rstrip('\r\n').rsplit(',', len(time)+3)
		# get region
		region = line[1]
		# initialize region if needed
		if not(region in data_by_region.keys()):
			data_by_region[region] = [0]*len(time)
		# add data to region
		for i, data in enumerate(line[4:]):
			try: data_by_region[region][i]+= int(data)
			except: data_by_region[region][i]+= 0
	# output
	return time, data_by_region
#_______________________________________________________________________________
#
def read_data_dpc(rawdata):
	"""
	"""
	# modules
	import os
	import datetime as dt
	# path to time-series files
	timeseries_path = os.path.join(rawdata.path, 'dati-regioni')
	# read confirmed cases
	timeseries_file = os.path.join(timeseries_path, 'dpc-covid19-ita-regioni.csv')
	# initilize output
	time      = []
	confirmed = {}
	recovered = {}
	deaths    = {}
	active    = {}
	intensive = {}
	# open file
	f = open(timeseries_file, 'r')
	# skip header
	f.readline()
	# loop on entries
	for l in f:
		# split line
		line = l.rstrip('\r\n').rsplit(',')
		# get time
		t = dt.datetime.strptime(line[0], '%Y-%m-%d %H:%M:%S')
		t = dt.datetime(*t.timetuple()[:3])
		if not(t in time): time.append(t)
		# get region name
		region = line[3]
		# get confirmed
		if not(region in confirmed.keys()): confirmed[region]=[0]*(len(time)-1)
		confirmed[region]+= [int(line[14])]
		# get recovered
		if not(region in recovered.keys()): recovered[region]=[0]*(len(time)-1)
		recovered[region]+= [int(line[12])]
		# get deaths
		if not(region in deaths.keys()): deaths[region]=[0]*(len(time)-1)
		deaths[region]+= [int(line[13])]
		# get active
		if not(region in active.keys()): active[region]=[0]*(len(time)-1)
		active[region]+= [int(line[10])]
		# get intensive
		if not(region in intensive.keys()): intensive[region]=[0]*(len(time)-1)
		intensive[region]+= [int(line[7])]
	# output
	return time, confirmed, recovered, deaths, active, intensive
#_______________________________________________________________________________
#
def read_data_ofr(rawdata):
	"""
	"""
	# modules
	import os
	import datetime as dt
	# path to time-series files
	timeseries_path = os.path.join(rawdata.path, 'dist')
	# read confirmed cases
	timeseries_file = os.path.join(timeseries_path, 'chiffres-cles.csv')
	# initilize output
	time      = []
	confirmed = {}
	recovered = {}
	deaths    = {}
	active    = {}
	intensive = {}
	# open file
	f = open(timeseries_file, 'r')
	# skip header
	f.readline()
	# loop on entries
	for l in f:
		# split line
		line = l.rstrip('\r\n').rsplit(',')
		line = ['0' if c == '' else c for c in line]
		if ('REG' in line[2])|('FRA' in line[2]):
			if ('et de la Sant' in line[9])|('ARS' in line[9]):
				# get time
				t = dt.datetime.strptime(line[0], '%Y-%m-%d')
				t = dt.datetime(*t.timetuple()[:3])
				if not(t in time): time.append(t)
				# get region name
				region = line[3]
				# get confirmed
				if not(region in confirmed.keys()): confirmed[region]=[]
				confirmed[region]+= [0]*(len(time)-len(confirmed[region])-1)
				confirmed[region]+= [int(line[4])]
				# get deaths
				if not(region in deaths.keys()): deaths[region]=[]
				deaths[region]+= [0]*(len(time)-len(deaths[region])-1)
				deaths[region]+= [int(line[5])]
				# get intensive
				if not(region in intensive.keys()): intensive[region]=[]
				intensive[region]+= [0]*(len(time)-len(intensive[region])-1)
				intensive[region]+= [int(line[6])]
				# get recovered
				if not(region in recovered.keys()): recovered[region]=[]
				recovered[region]+= [0]*(len(time)-len(recovered[region])-1)
				recovered[region]+= [int(line[8])]
				# initialize active
				if not(region in active.keys()): active[region]=[]
	# fix_data
	fix_data_ofr(time, confirmed)
	fix_data_ofr(time, deaths)
	fix_data_ofr(time, recovered)
	# compute active
	for region, data in active.iteritems():
		active[region] = [c-r-d for c, r, d in zip(confirmed[region], deaths[region],  recovered[region])]
	# output
	return time, confirmed, recovered, deaths, active, intensive
#_______________________________________________________________________________
#
def fix_data_ofr(time, data_dict):
	for region, data in data_dict.iteritems():
		for i, point in enumerate(data):
			if i == 0: mindata = point
			elif point < mindata:
				data_dict[region][i]=mindata
			else: mindata = point
	return data
#_______________________________________________________________________________
#
