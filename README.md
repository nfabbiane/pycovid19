# COVID-19 STATISTICS

Light visualisation tool in Python for the statics of COVID-19 spreading

(2020) Nicolo Fabbiane

* * *


## Usage

To visualize the statistics, run the command:
	
	make data=<data-set-name>
	
or
	
	python3 visualize.py <data-set-name>
	

The visualisation parameters set in the initial part of the script.
By default, the John-Hopkins Univerity data are used; the script handles
the download of the data from the specified github repository.

To clean the repository form the downloaded data, run the command:
	
	make clean
	
