from flask import Flask, render_template, request
from logging.handlers import RotatingFileHandler
from elasticsearch import Elasticsearch
from datetime import datetime
import logging

app = Flask(__name__)
app.debug = True
es = Elasticsearch('127.0.0.1', port=9200)
res = {}
relevant_ids = []



@app.route('/')
def home():
    return render_template("search.html")


@app.route('/search/results', methods=['POST'])
def search_request():
    if request.values.get('docid'):
        id = request.values.get('docid')
        checked = request.values.get('checked')
        if checked=='true':
            relevant_ids.append(id)
            app.logger.info(str(datetime.now()) + ": " + "Marked " + id + " as relevant")
        else:
            relevant_ids.remove(id)
            app.logger.info(str(datetime.now()) + ": " + "Unmarked " + id + " as relevant")
        print('relevant ids: ', relevant_ids)
    else:
        search_term = request.form["input"]
        global res
        res = es.search(
            index="aquaint",
            size=10,
            body={
                "query": {
                    "multi_match" : {
                        "query": search_term,
                        "fields": [
                            "headline",
                            "body"
                     ]
                 }
             }
        }

        )
        app.logger.info(str(datetime.now()) + ": Entered query: " + search_term)
    # res = es.search(index="test-index", body={"query": {"match_all": {}}})
    print("Got %d Hits:" % res['hits']['total'])
    return render_template('results.html', res=res, relevant_ids=relevant_ids )


@app.route('/view/<docid>')
def view_result(docid):
    res = es.search(
        index="aquaint",
        size=1,
        body={
            "query": {
                "match": {
                    "_id": docid
                }
            }
        }
    )
    result = res['hits']['hits'][0]
    result['_source']['body'][0] = result['_source']['body'][0].replace('<p>', '')
    result['_source']['body'][0] = result['_source']['body'][0].replace('</p>', '')

    return render_template('view.html', res=result)


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    handler = RotatingFileHandler('engine.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5000)