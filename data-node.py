###############################################################################
#
# Filename: data-node.py
# Author: Jose R. Ortiz and Sofia I. Crespo Maldonado
#
# Description:
# 	data node server for the DFS
#

from Packet import *
from mds_db import * #SICM

import sys
import socket
import socketserver
import uuid
import os.path

def usage():
	print ("""Usage: python %s <server> <port> <data path> <metadata port,default=8000>""" % sys.argv[0] )
	sys.exit(0)


def register(meta_ip, meta_port, data_ip, data_port):
	"""Creates a connection with the metadata server and
	   register as data node
	"""

	# Establish connection
	md = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #SICM
	md.connect((meta_ip, meta_port)) #SICM

	# Create an object of type mds_db
	db = mds_db("dfs.db") #SICM

	# Connect to the database
	print("Connecting to database") #SICM
	db.Connect() 	#SICM

	try:
		response = "NAK"
		sp = Packet()
		while response == "NAK":
			sp.BuildRegPacket(data_ip, data_port)
			md.sendall(bytes(sp.getEncodedPacket(), 'utf-8'))
			response = md.recv(1024)

			if response.decode('utf-8') == "DUP":
				return print ("Duplicate Registration")

			if response.decode('utf-8') == "NAK":
				return print ("Registration ERROR")

	finally:
		md.close()
	

class DataNodeTCPHandler(socketserver.BaseRequestHandler):

	def handle_put(self, p):

		"""Receives a block of data from a copy client, and 
		   saves it with an unique ID.  The ID is sent back to the
		   copy client.
		"""

		fname, fsize = p.getFileInfo()

		# Generates an unique block id.
		blockid = str(uuid.uuid1())

		# Open the file for the new data block.  
		file_name = DATA_PATH + blockid
		temp_file = open(file_name, "wb")

		if (not temp_file):
			self.request.sendall(bytes("NOP", 'utf-8'))
			return 0
		
		self.request.sendall(bytes("OK", 'utf-8'))

		buffer_size = 1024

		# Receive the data block.
		while temp_file.tell() < fsize:
			content = self.request.recv(buffer_size)
			temp_file.write(content)

		temp_file.close()

		sp = Packet()
		sp.BuildGetDataBlockPacket(blockid)

		# Send the block id back
		self.request.sendall(bytes(sp.getEncodedPacket(), 'utf-8')) #SICM

	def handle_get(self, p):
		
		# Get the block id from the packet
		blockid = p.getBlockID()

		# Construct file name to look for data block
		fname = DATA_PATH+blockid
		fsize = os.path.getsize(fname)

		self.request.sendall(bytes(str(fsize), 'utf-8'))

		rec = self.request.recv(1024)
		
		if rec.decode('utf-8') == "NOP":
			return print("File size wasn't received")

		file = open(fname, "rb") #SICM

		# Read the file with the block id data
		section = file.read() #SICM

		# Send it back to the copy client.
		self.request.sendall(section)

	def handle(self):
		msg = self.request.recv(1024)
		print (msg, type(msg))

		p = Packet()
		p.DecodePacket(msg)

		cmd = p.getCommand()
		if cmd == "put":
			self.handle_put(p)

		elif cmd == "get":
			self.handle_get(p)
		

if __name__ == "__main__":

	META_PORT = 8000
	if len(sys.argv) < 4:
		usage()

	HOST = sys.argv[1]
	PORT = int(sys.argv[2])
	DATA_PATH = sys.argv[3]

	if (len(sys.argv) > 4):
		META_PORT = int(sys.argv[4])

	if not os.path.isdir(DATA_PATH):
		print ("Error: Data path %s is not a directory." % DATA_PATH)
		usage()
	
	"""try:
		HOST = sys.argv[1]
		PORT = int(sys.argv[2])
		DATA_PATH = sys.argv[3]

		if len(sys.argv > 4):
			META_PORT = int(sys.argv[4])

		if not os.path.isdir(DATA_PATH):
			print ("Error: Data path %s is not a directory." % DATA_PATH)
			usage()
	except:
		usage()"""


	register("localhost", META_PORT, HOST, PORT)
	server = socketserver.TCPServer((HOST, PORT), DataNodeTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
	server.serve_forever()
