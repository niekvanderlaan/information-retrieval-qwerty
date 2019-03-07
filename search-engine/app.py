from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
import webbrowser

app = Flask(__name__)
es = Elasticsearch('127.0.0.1', port=9200)
res = {}

@app.route('/')
def home():
    return render_template("search.html")


@app.route('/search/results', methods=['GET', 'POST'])
def search_request():
    search_term = request.form["input"]
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
    # res = es.search(index="test-index", body={"query": {"match_all": {}}})
    print("Got %d Hits:" % res['hits']['total'])
    return render_template('results.html', res=res )


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
    print(result)
    return render_template('view.html', res=result)


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host='0.0.0.0', port=5000)