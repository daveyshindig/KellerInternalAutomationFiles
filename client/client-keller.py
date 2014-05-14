#---------------------------------
# Author: Christian Damo
# Date: 2014-05-08
#---------------------------------

import os
import csv
import shutil
import subprocess
import sys
import xmlrpclib

server = xmlrpclib.Server('http://128.171.152.55:9000')
inputFile = open("archive.csv","r")
reader=csv.reader(inputFile)

#get a list of directories in the folder
directories = os.walk('.').next()[1]
#directories.remove("archive")
archivedDirectories = reader.next()
inputFile.close()
outputFile=open("archive.csv","wb")
writer = csv.writer(outputFile)
newRow = list(archivedDirectories)

for archivedDirectory in archivedDirectories:
	directories.remove(archivedDirectory)


#check to see if it is an active or non active log
#by checking to see if there's 4 or 6 files
for directory in directories:
	files = os.listdir(directory)

	#if a folder is found with 6 files transfer it over to the server
	if len(files) == 6:
		#transfer the files over
		for file_ in files:
			path = os.path.join(directory,file_)
			with open(path,"rb") as handle:
				binary_data = xmlrpclib.Binary(handle.read())
				server.push_file_to_server(binary_data,directory,file_)
				handle.close()
				
	#archive folder
	newRow.append(directory)
	
writer.writerow(newRow)
outputFile.close()


			

