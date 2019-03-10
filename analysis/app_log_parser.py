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
    actions_per_query = {}
    lines = f.readlines()
    for line in lines:
        print(line)
        z = re.match("\d{4}\-\d{2}\-\d{2}\s(\d{2}:\d{2}:\d{2}).\d{6}:\s(\w*?\s\w*?):\s(.*?)$", line)
        if not z:
            print("No match at line: ", line)
            continue
        groups = z.groups()
        time = groups[0]
        action = groups[1].split(" ")
        value = groups[2]

        if action[0] == "Entered":
            actions_per_query[value] = {
                "num_relevant": 0,
                "num_clicked": 0,
            }





