#do a dir system call

import os
import subprocess

directories = os.walk('.').next()[1]
#print directories
#blah = os.path.join(directories[0],".")
#print os.walk(blah).next[1]
#got to figure out how to call the folder.
#call >>python "pathname to voltage/current files" in the form of floder\folder\filename

#subprocess.call(["gvim",os.path.join(directories[0],"Voltage_meta.txt")])
for directory in directories:
	if "~" not in directory:
		print "working on "+directory+" files"
		subprocess.call(["python","extractData_r2cd.py",directory])
	#and then the extract script incorporates the diretory so that it 
	# follows soething like
	# inputFileName = os.path.join(directory,"Voltage_meta.txt")
