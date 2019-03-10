import argparse
import os
import sys
import re

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('source', help='Text file with app logs for one topic')
parser.add_argument('destination', help='Target file for analysis')
args = parser.parse_args()

# check input is valid
if not os.path.isfile(args.source):
    print("Please specify a valid source file")
    sys.exit(1)

# check output is defined
if not args.destination:
    print("Please specify a destination file")
    sys.exit(1)

with open(args.source) as f:
    queries = []
    num_clicked = 0
    num_relevant = 0

    time_of_query = False
    lines = f.readlines()

    #Loop over each line
    for line in lines:
        z = re.match("\d{4}\-\d{2}\-\d{2}\s(\d{2}:\d{2}:\d{2}).\d{6}:\s(\w*?\s\w*?):\s(.*?)$", line)
        if not z:
            print("No match at line: ", line)
            continue
        groups = z.groups()
        time = groups[0]
        action = groups[1].split(" ")
        value = groups[2]

        if action[0] == "Entered":
            queries.append(value)

            if not time_of_query:
                print("first query")


            continue


        if action[0] == "Clicked":
            num_clicked = num_clicked + 1
            continue

        if action[0] == "Marked":
            if action[1] == "relevant":
                num_relevant = num_relevant + 1
            else:
                num_relevant = num_relevant - 1

    #End of lines

    num_queries = len(queries)

    with open(args.destination, "w+") as d:
        d.write("#Queries: " + str(num_queries) + "\n")
        d.write("#Relevant: "+ str(num_relevant) + "\n")
        d.write("#Clicked: " + str(num_clicked) + "\n")












