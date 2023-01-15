###############################################################################
#
# Filename: copy.py
# Author: Jose R. Ortiz and Sofia I. Crespo Maldonado
#
# Description:
# 	Copy client for the DFS
#
#

import socket
import sys
import os.path

from Packet import *

def usage():
	print ("""Usage:\n\tFrom DFS: python %s <server>:<port>:<dfs file path> <destination file>\n\tTo   DFS: python %s <source file> <server>:<port>:<dfs file path>""" % (sys.argv[0], sys.argv[0]))
	sys.exit(0)

def copyToDFS(address, fname, path): #fname = to_path, path = from_path
	""" Contact the metadata server to ask to copy file fname,
	    get a list of data nodes. Open the file in path to read,
	    divide in blocks and send to the data nodes. 
	"""

	# Create a connection to the data server

	# Establish connection
	md = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #SICM
	md.connect((address[0], address[1])) #SICM

	# Read file
	fsize = os.path.getsize(path) #SICM


	# Create a Put packet with the fname and the length of the data,
	# and sends it to the metadata server 

	sp = Packet() #SICM
	sp.BuildPutPacket(fname, fsize) #SICM
	md.sendall(bytes(sp.getEncodedPacket(), 'utf-8')) #SICM


	# If no error or file exists
	# Get the list of data nodes.
	# Divide the file in blocks
	# Send the blocks to the data servers

	response = md.recv(1024) #SICM

	if response.decode('utf-8') == "DUP": #SICM
		return print("File already exists") #SICM

	md.close()

	# Define a packet object to decode packet messages
	p = Packet() #SICM
	
	# Decode the packet received
	p.DecodePacket(response) #SICM

	servers = p.getDataNodes() #SICM
	print("Available data nodes")
	print(servers) #SICM

	block_size = fsize//len(servers) #SICM
	
	# Read file into blocks
	file = open(path, "rb") #SICM

	section = file.read(block_size) #SICM

	i = 0
	pack = Packet()

	block_list = []


	while section and i < len(servers):

		# Establish connection to data node
		pack.BuildPutPacket(fname, len(section))
		dn = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #SICM
		dn.connect((servers[i][0], servers[i][1])) #SICM
		dn.sendall(bytes(pack.getEncodedPacket(), 'utf-8')) #SICM

		rec = dn.recv(1024)
		if rec.decode('utf-8') == "NOP":
			return print("File can't be opened")
		if rec.decode('utf-8') == "OK":
			dn.sendall(section)

		response = dn.recv(1024) #SICM

		# Define a packet object to decode packet messages
		pp = Packet() #SICM
	
		# Decode the packet received
		pp.DecodePacket(response) #SICM

		bid = pp.getBlockID()

		# Filling block list
		block_list.append((servers[i][0], servers[i][1], bid))

		# For the last server, read the remaining bytes of a file
		if (i == len(servers)-2):
			section = file.read()
		else: section = file.read(block_size)
		i += 1
		dn.close()

	file.close()
		
	bpack = Packet()
	bpack.BuildDataBlockPacket(fname, block_list)

	# Establish connection
	mdt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #SICM
	mdt.connect((address[0], address[1])) #SICM

	# Notify the metadata server where the blocks are saved.

	mdt.sendall(bytes(bpack.getEncodedPacket(), 'utf-8')) #SICM

	
def copyFromDFS(address, fname, path):
	""" Contact the metadata server to ask for the file blocks of
	    the file fname.  Get the data blocks from the data nodes.
	    Saves the data in path.
	"""

   	# Contact the metadata server to ask for information of fname

	# Establish connection
	md = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #SICM
	md.connect((address[0], address[1])) #SICM

	sp = Packet() #SICM
	sp.BuildGetPacket(fname) #SICM
	md.sendall(bytes(sp.getEncodedPacket(), 'utf-8')) #SICM

	# If there is no error response Retreive the data blocks
	response = md.recv(1024) #SICM

	if response.decode('utf-8') == "NFOUND": #SICM
		return print("File not found") #SICM

	md.close()

    # Save the file
	
	# Define a packet object to decode packet messages
	pp = Packet() #SICM
	
	# Decode the packet received
	pp.DecodePacket(response)

	block_list = pp.getDataNodes()

	file_name = path
	new_file = open(file_name, "wb")

	

	# LOOP TO ACCESS EACH DATANODE AND RETRIEVE FILE CHUNK
	
	for address, port, block_id in block_list:

		# Build packet and connect to data node
		pp.BuildGetDataBlockPacket(block_id) #SICM
		dn = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #SICM
		dn.connect((address, port)) #SICM

		dn.sendall(bytes(pp.getEncodedPacket(), 'utf-8')) #SICM

		buffer_size = 1024

		# Receive size of the data block
		rec = dn.recv(1024)
		fsize = int(rec.decode('utf-8'))

		if (not fsize):
			dn.sendall(bytes("NOP", 'utf-8'))
			return 0
		else: 
			dn.sendall(bytes("OK", 'utf-8'))

		# Write to output file
		written_bytes = 0
		while written_bytes < fsize:
			prev = new_file.tell()

			response = dn.recv(buffer_size) #SICM
			new_file.write(response)
			written_bytes+=new_file.tell()-prev

		dn.close()
	print(file_name, "has been created")



if __name__ == "__main__":
#	client("localhost", 8000)
	if len(sys.argv) < 3:
		usage()

	file_from = sys.argv[1].split(":")
	file_to = sys.argv[2].split(":")

	if len(file_from) > 1:
		ip = file_from[0]
		port = int(file_from[1])
		from_path = file_from[2]
		to_path = sys.argv[2]

		if os.path.isdir(to_path):
			print ("Error: path %s is a directory.  Please name the file." % to_path)
			usage()

		copyFromDFS((ip, port), from_path, to_path)

	elif len(file_to) > 2:
		ip = file_to[0]
		port = int(file_to[1])
		to_path = file_to[2]
		from_path = sys.argv[1]

		if os.path.isdir(from_path):
			print ("Error: path %s is a directory.  Please name the file." % from_path)
			usage()

		copyToDFS((ip, port), to_path, from_path)


