###############################################################################
#
# Filename: ls.py
# Author: Jose R. Ortiz and Sofia I. Crespo Maldonado
#
# Description:
# 	List client for the DFS
#



import socket
import sys

from Packet import *

def usage():
	print ("""Usage: python %s <server>:<port, default=8000>""" % sys.argv[0]) 
	sys.exit(0)

def client(ip, port):

	# Contacts the metadata server and ask for list of files.

	# Establish connection
	md = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #SICM
	md.connect((ip, port)) #SICM

	sp = Packet() #SICM
	sp.BuildListPacket() #SICM
	md.sendall(bytes(sp.getEncodedPacket(), 'utf-8')) #SICM
	response = md.recv(1024) #SICM

	# Define a packet object to decode packet messages
	p = Packet()
	
	# Decode the packet received
	p.DecodePacket(response)

	files = p.getFileArray()

	# Print files stored in database
	for i in range(len(files)):
		name = files[i][0]
		size = files[i][1]
		print(name, size, "bytes")

	md.close()



if __name__ == "__main__":

	if len(sys.argv) < 2:
		usage()

	ip = None
	port = None 
	server = sys.argv[1].split(":")
	if (len(server) == 1):
		ip = server[0]
		port = 8000
	elif (len(server) == 2):
		ip = server[0]
		port = int(server[1])

	if not ip:
		usage()

	client(ip, port)
