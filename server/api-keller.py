#----------------------
# Author: Christian Damo
# Date: 2014-05-08
#----------------------

from SimpleXMLRPCServer import SimpleXMLRPCServer
import psycopg2
import sys
import datetime
import os
import subprocess

address = ("", 9000)
server = SimpleXMLRPCServer(address)

def hello_world(name):
	return "Hello World, How are you doing " + name + "?"
server.register_function(hello_world)

def server_receive_file(arg):
	with open("output","wb") as handle:
		handle.write(arg.data)
		return True
server.register_function(server_receive_file)

def push_file_to_server(arg,directory,filename):
	#check to see if the directory exists
	#get list of directories
	directories = os.walk('.').next()[1]
	#check to see if directory is in directories
	if directory not in directories:
		subprocess.call(["mkdir",directory])
	path = os.path.join(directory,filename)
	with open(path,"wb") as handle:
		handle.write(arg.data)
		return True
server.register_function(push_file_to_server)

try:
	print "serving..."
	server.serve_forever()
except KeyboardInterrupt:
	print "stopping!"
	server.server_close()
