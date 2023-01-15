Sofia I. Crespo Maldonado
Assignment 4: Distributed File System
CCOM4017: Operating Systems
Prof. Jose R. Ortiz-Ubarri

Note: Please run using the mds_db.py in my file as the AddDataNode function has
a slight change from the original and . Also, run on Python 3 as the contents 
have been adapted for this version (even in the Packet.py). 

CONTENTS
--------

- Introduction
- Prerequisites
- Metadata Server
- Data Node Server
- List Client
- Copy Client
- Creating an Empty Database
- Resources

INTRODUCTION
------------

This project is an implementation of a simple Distributed File System. It
includes the following components: a metadata server as an inode repository,
data servers as disk space for file data blocks, a list client to list files in
the DFS, and a copy client that will copy files from and to the DFS.


PREREQUISITES
-------------

- Python: www.python.org
- Python socketserver library: for the socket communication. 
	https://docs.python.org/2/library/socketserver.html
- uuid: to generate unique IDs for the data blocks
	https://docs.python.org/2/library/uuid.html
- Optionally you may read about the json and sqlite3 libraries used in the
 skeleton of the program.
	https://docs.python.org/2/library/json.html
	https://docs.python.org/2/library/sqlite3.html


METADATA SERVER
---------------

The metadata server is in charge of:
- registering the data nodes to database
- listen to client requests
	- list files in database
	- check if a file is in DFS and return nodes with block ids that contain
		the file in order to read it
	- insert new file to database, return available data nodes and store data
		blocks that have the block ids and information of data nodes of the
		file

Must be run as follows:
	python meta-data.py <port, default=8000>

Example:
	python meta-data.py 4017


DATA NODE SERVER
----------------

The data node server is in charge of:
- register with metadata server on execution
- receive blocks of data, store them with an unique id and return the id
- receive data block requests, read and return its content

Must be run as follows:
	python data-node.py <server address> <port> <data path> <metadata port,default=8000>

Server address is the metadata server address, port is the data-node port number,
data path is a path to a directory to store the data blocks, and metadata port
is the optional metadata port if it was run in a different port other than the
default port.

Example:
	python data-node.py localhost 2020 C: 4017


LIST CLIENT
-----------

The list client is in charge of:
- sending a list request to the metadata server
- receiving and displaying the files in the database and their size

Expected output:
	newfile.txt 91 bytes
	loona.jpeg 430346 bytes

Must be run as follows:
	python ls.py <server>:<port, default=8000>

Server and port are the metadata server address and optional port if it was run 
in a different port other than the default port.

Example:
	python ls.py localhost:4017


COPY CLIENT
-----------
The copy client is in charge of:
- writing files to the DFS
	- send to metadata server the name and size of the file and receive the
		list of available data nodes
	- send the data blocks to each data node
- reading files from the DFS
	- contact metadata server with the file to read, receive the block list,
		and retrieve file blocks from the data servers

Must be run as follows:
	- To write to DFS
		python copy.py <source file> <server>:<port>:<dfs file path>

		Where server is the metadata server IP address, port is the
		metadata server port, source file is the input file name, anf dfs
		file path is how it will be stored in the database.
	
		Example:
			python copy.py flipthat.jpeg localhost:4017:loona.jpeg

	- To read from DFS
		python copy.py <server>:<port>:<dfs file path> <destination file>

		Where server is the metadata server IP address, port is the
		metadata server port, dfs file path is the file name in the database,
		and destination file will be the name of the output file (always
		include the extension of the destination file)

		Example: python copy.py localhost:4017:loona.jpeg dalso.jpeg


CREATING AN EMPTY DATABASE
--------------------------

The script createdb.py generates an empty database dfs.db for the project.

Must be run as follows:
	python createdb.py


RESOURCES
---------

- https://codeonby.com/2022/03/12/split-file-into-byte-chunks-in-python/
- https://www.educative.io/answers/how-to-convert-strings-to-bytes-in-python
- https://bobbyhadz.com/blog/python-attributeerror-dict-object-has-no-attribute-has-key
- https://stackoverflow.com/questions/606191/convert-bytes-to-a-string
- https://stackoverflow.com/questions/15210178/python-socket-programming-oserror-winerror-10038-an-operation-was-attempted-o
- https://stackoverflow.com/questions/283707/size-of-an-open-file-object