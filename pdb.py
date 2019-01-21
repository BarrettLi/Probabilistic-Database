from Parser import Parser
from lifted_inference import *
from query2sql import *
import time
def main():
    parser = Parser()
    parser.connect()
    parser.parse()
    startTime = time.time()
    lifted_query = perform_inference_dnf(parser.queries[0])
    if lifted_query:
        print("\nLifted Query:")
        print(lifted_query.tostring())
        v = sqlVistor()
        sql_query = lifted_query.accept(v)
        print("\nSQL Query:")
        print(sql_query)
        parser.cur.execute(sql_query + ";")
        print("Result probability:")
        for record in parser.cur:
            if record[0]:
                print(record[0])
            else:
                print("Calculation has failed. Probably due to nonexistent table.")
    else:
        print("\n Query is unliftable.")
    print("\n Execution Time of lifting and querying (if query was liftable): " +
          str(time.time() - startTime))
    parser.close()

if __name__ == '__main__':
   main()
