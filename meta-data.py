###############################################################################
#
# Filename: meta-data.py
# Author: Jose R. Ortiz and Sofia I. Crespo Maldonado
#
# Description:
# 	MySQL support library for the DFS project. Database info for the 
#       metadata server.
#
# Please modify globals with appropiate info.

from mds_db import *
from Packet import *
import sys
import socketserver

def usage():
	print ("""Usage: python %s <port, default=8000>""" % sys.argv[0] )
	sys.exit(0)


class MetadataTCPHandler(socketserver.BaseRequestHandler):

	def handle_reg(self, db, p):
		"""Register a new client to the DFS  ACK if successfully REGISTERED
			NAK if problem, DUP if the IP and port already registered
		"""

		try:
			if (db.AddDataNode(p.getAddr(), p.getPort())): #SICM
				print("Node Added:", p.getAddr(), ":") #SICM): # Fill condition: SICM
				self.request.sendall(bytes("ACK", 'utf-8'))
			else:
				self.request.sendall(bytes("DUP", 'utf-8'))
		except:
			self.request.sendall(bytes("NAK", 'utf-8'))


	def handle_list(self, db):
		"""Get the file list from the database and send list to client"""
		
		try:
			sp = Packet() #SICM

			files = [] #SICM
			for file, size in db.GetFiles(): #SICM
				files.append((file,size)) #SICM

			sp.BuildListResponse(files)#SICM

			self.request.sendall(bytes(sp.getEncodedPacket(), 'utf-8'))

		except:
			self.request.sendall(bytes("NAK", 'utf-8'))

	def handle_put(self, db, p):
		"""Insert new file into the database and send data nodes to save
           the file.
        """

		sp = Packet() #SICM
		info = p.getFileInfo() #SICM
        
		if db.InsertFile(info[0], info[1]):

		#GET AVAILABLE DATA NODES AND SEND TO DATA NODE
			metalist = [] #SICM
			for address, port in db.GetDataNodes(): #SICM
				metalist.append((address, port)) #SICM
			sp.BuildPutResponse(metalist) #SICM
			self.request.sendall(bytes(sp.getEncodedPacket(), 'utf-8')) #SICM
		else:
			self.request.sendall(bytes("DUP", 'utf-8'))
	
	def handle_get(self, db, p):
		"""Check if file is in database and return list of
			server nodes that contain the file.
		"""

		# Fill code to get the file name from packet and then 
		# get the fsize and array of metadata server
		fname = p.getFileName()
		fsize, blocks = db.GetFileInode(fname)
		
		# If file is in dataset, send size and block list
		if fsize:
			sp = Packet()
			sp.BuildGetResponse(blocks, fsize)
			self.request.sendall(bytes(sp.getEncodedPacket(), 'utf-8'))
		else:
			self.request.sendall(bytes("NFOUND", 'utf-8'))

	def handle_blocks(self, db, p):
		"""Add the data blocks to the file inode"""

		# Fill code to get file name and blocks from
		# packet
		fname = p.getFileName()
		blocks = p.getDataBlocks()
	
		# Fill code to add blocks to file inode
		db.AddBlockToInode(fname, blocks)

		
	def handle(self):

		# Establish a connection with the local database
		db = mds_db("dfs.db")
		db.Connect()

		# Define a packet object to decode packet messages
		p = Packet()

		# Receive a msg from the list, data-node, or copy clients
		msg = self.request.recv(1024)
		print (msg, type(msg))
		
		# Decode the packet received
		p.DecodePacket(msg)
	
		# Extract the command part of the received packet
		cmd = p.getCommand()

		# Invoke the proper action 
		if   cmd == "reg":
			# Registration client
			self.handle_reg(db, p)

		elif cmd == "list":
			# Client asking for a list of files
			# Fill code
			self.handle_list(db) #SICM

		elif cmd == "put":
			# Client asking for servers to put data
			# Fill code
			self.handle_put(db, p) #SICM
		
		elif cmd == "get":
			# Client asking for servers to get data
			# Fill code
			self.handle_get(db, p) #SICM

		elif cmd == "dblks":
			# Client sending data blocks for file
			 # Fill code
			self.handle_blocks(db, p) #SICM

		db.Close()

if __name__ == "__main__":
	HOST, PORT = "", 8000
	
	if (len(sys.argv) > 1):
		try:
			PORT = int(sys.argv[1])
		except:
			usage()

	server = socketserver.TCPServer((HOST, PORT), MetadataTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
	server.serve_forever()
