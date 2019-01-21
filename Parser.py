#!/usr/bin/env python

import getopt, sys, psycopg2
import query as Query
import time


class Parser:
    conn = None # connection with backend database
    cur = None # cursor with database
    queries = [] # contains a list of queries

    def connect(self):
        try:
            self.conn = psycopg2.connect("dbname='template1' user='postgres' host='localhost' password='password'" )
            self.cur = self.conn.cursor()
        except:
            print("I am unable to connect to the database")
        # clean all existed tables
        query = "DROP SCHEMA public CASCADE;"
        self.cur.execute(query)
        query = "CREATE SCHEMA public;"
        self.cur.execute(query)
        self.conn.commit()
        print("Delete all existed tables")

    def parse(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:],"", ["query=", "table="])
        except getopt.GetoptError as err:
            print(str(err))
            sys.exit(2)
        # print(opts)
        opts.sort(key=lambda tup: tup[0], reverse=True)
        for o, a in opts:
            if o == "--table":
                self.parseTable(a)
                print("Table " + a + " read")
            if o == "--query":
                self.parseQuery(a)
                print("Query " + a + " read")

    def parseTable(self, fname):
        with open(fname) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        table_name = content[0]
        content = [x.split(',') for x in content[1:]]

        var_num = len(content[0])

        # create a table
        query = "CREATE TABLE IF NOT EXISTS " + table_name + " (\n"
        for i in range(var_num-1):
            query = query + 'col' + str(i) + " INTEGER, \n"
        query = query + "p FLOAT);\n"
        self.cur.execute(query)

        # load table
        for x in content:
            # print(",".join(x))
            query = "INSERT INTO " + table_name + " VALUES (" + ",".join(x) + ");"
            self.cur.execute(query)

        # commit queries to database
        self.conn.commit()

    def parseQuery(self, fname):
        with open(fname) as f:
            # read one query at a time
            for line in f:
                # eliminate space in string
                query = line.replace(" ", "")
                # split by disjunction symbol "||"
                conjs = query.split("||")
                conj_objs = []
                for conj in conjs:
                    # for each conjunction, split by conjunction symbol ","
                    tables = conj.split("),")
                    tuple_objs = []
                    for table in tables:
                        # for each table
                        negate = False
                        # check if it is negated
                        if table.startswith("~"):
                            negate = True
                            # get rid of negate symbol
                            table = table[1:]
                        # i.e. R(x1,y1) --> [R, x1, y1]
                        table = table.replace("(", ",").replace(")", " ").strip().split(",")

                        # create a table (deals with nonexistent table case)
                        # remove if nonexistent table edge case is not tested
                        query = "CREATE TABLE IF NOT EXISTS " + table[0] + " (\n"
                        for i in range(len(table)-1):
                            query += 'col' + str(i) + " INTEGER, \n"
                        query += "p FLOAT);\n"
                        self.cur.execute(query)
                        self.conn.commit()

                        # create tuple objects
                        tuple_objs.append(Query.Tuple([Query.Variable(x, is_constant=True if x.isdigit() else False) for x in table[1:]], table[0], negate))
                    conj_objs.append(Query.Conj(tuple_objs))
                self.queries.append(Query.Disj(conj_objs))

    def close(self):
        query = "DROP SCHEMA public CASCADE;"
        self.cur.execute(query)
        query = "CREATE SCHEMA public;"
        self.cur.execute(query)
        self.conn.commit()
        print("Clean up backend database")
        self.cur.close()
        self.conn.close()
        print("Close connection")

# example codes:
if __name__ == '__main__':
    startTime = time.time()
    parser = Parser()
    parser.connect()
    parser.parse()
    for q in parser.queries:
        print(q.tostring())
    executionTime = time.time() - startTime
    print("Execution time was: " + repr(executionTime) + " seconds.")
    parser.close()
