CS 267A Probabilistic Database Project
==================================================
Requirements
==================================================
Python 3.6

Python Libraries:
psycopg2 (PostGreSQL backend)
numpy (for unionfind.py; to perform Step 1 of the lifting algorithm)

Requires PostGreSQL installed (ver 11.1 used), and assumes default database
connection settings when prompted upon installation:
user=postgres
host=localhost
password=password

==================================================
Files
==================================================
pdb.py:
Run this file with the selected flags and files to run the algorithm on the
selected queries and files with the given command line format (as was
specified):
python3 ./pdb.py --query query.txt --table t1.txt --table t2.txt --table t3.txt

lifted_inference.py:
Transforms parsed query from a query .txt file into an expression that is later
evaluated into a probability.

lifted_inference_util.py:
Contains the implementation of various conversions performed within
lifted_inference.py.

lifted_inference_util_test.py:
Tests lifted_inference_util.py.

lifted_inference_test.py:
Tests lifted_inference.py.

Parser.py:
Contains the main implementation of parsing table .txt files into SQL queries
which create tables upon execution and query .txt files into a query to be
lifted after all tables are created.

query.py:
Class definitions of the which make up the structure of the lifted query.

query2sql.py:
Contains the implementation for the conversion of the lifted query into an
executable SQL query that returns a numeric probability. If a nonexistent table
is queried, it throws an error.

unionfind.py:
Manages disjoint subsets, mainly used in the conversion to UCNF.

testCases/:
Contains various test cases for testing the program. info.txt goes into what
each test case is trying to test.

In each test folder:
q.txt is the query of the test case
a.txt is what the answer should be
t*.txt are the table files
derivation*.png are the human-derived derivation of the query when lifted if
there is one