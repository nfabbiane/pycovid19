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
		self.time      = []
		self.confirmed = []
		self.recovered = []
		self.deaths    = []
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
		else: # default (John Hopkins University)
			data = read_data_jhu(self)
		# unpack data
		self.time      = data[0]
		self.confirmed = data[1]
		self.recovered = data[2]
		self.deaths    = data[3]
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
		# loop on regions
		for region in regions:
			if region in self.confirmed.keys():
				for i, data in enumerate(self.confirmed[region]):
					confirmed[i]+= data
			if region in self.recovered.keys():
				for i, data in enumerate(self.recovered[region]):
					recovered[i]+= data
			if region in self.deaths.keys():
				for i, data in enumerate(self.deaths[region]):
					deaths[i]+= data
		# output
		return confirmed, recovered, deaths
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
	# output
	return time, confirmed, recovered, deaths
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
	time = [dt.datetime.strptime(t, '%m/%d/%y').date() for t in line[4:]]
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
			data_by_region[region][i]+= int(data)
	# output
	return time, data_by_region
#_______________________________________________________________________________
#
