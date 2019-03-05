import argparse
import os
import sys
import re
import json
import glob
import traceback


from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from elasticsearch import helpers

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('folder', help='Folder with AQUAINT files')
parser.add_argument('--limit', '-l', type=int, default=0, help='limit number of files')
parser.add_argument('--index', '-i', default='aquaint', help='elastic index')
args = parser.parse_args()

# check input is valid
if not os.path.isdir(args.folder):
    print("Please specifiy a valid folder")
    sys.exit(1)

# limit files
files = []
for filename in glob.iglob(args.folder + '/**/*', recursive=True):
    if os.path.isfile(filename):
        files.append(filename)
if args.limit > 0:
    files = files[:args.limit]

print(len(files))
es = Elasticsearch(['127.0.0.1:9200'])

count = 0
data = []
for fname in files:
    print(fname)
    with open(fname) as f:
        content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        docs = soup.find_all('doc')
        actions = []
        for doc in docs:
            try:
                # only process news stories
                if doc.find('doctype') != None and doc.find('doctype').string.strip() != "NEWS STORY":
                    continue

                body = ""
                if doc.find('text').string != None:
                    body = doc.find('text').string.strip()
                if len(doc.find_all('p')) > 0:
                    body = "".join(['<p>{}</p>'.format(x.string) for x in doc.find_all('p')]),
                if body == "":
                    with open("empty_bodies.txt", "a") as ferr:
                        ferr.write(fname + "#" + doc.find('docno').string.strip() + "\n")
                actions.append({
                    '_index': args.index,
                    '_type': '_doc',
                    '_source': {
                        'docno': doc.find('docno').string.strip(),
                        # parse time and let Elastic know
                        'datetime': doc.find('date_time').string.strip() + ":00",
                        'headline': doc.find('headline').string.strip(),
                        'body': body
                    }
                })
                count += 1
            except Exception as e:
                with open("parse_errors.txt", "a") as ferr:
                    ferr.write(str(e) + "\n")
                    ferr.write(traceback.format_exc() + "\n")
                    ferr.write(str(doc))
        # with open(fname + '.json', 'w') as fp:
        #     print(fp)
        #     json.dump(actions, fp)
        helpers.bulk(es, actions)
    with open("processed_docs.txt", "a") as ferr:
        ferr.write(fname + "\n")

print("Total of {} documents processed".format(count))