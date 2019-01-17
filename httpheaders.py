import json
from collections import OrderedDict

from flask import Flask, request
from werkzeug.datastructures import Headers

from settings import HTTP_HEADERS_FILENAME, REMOVE_HEADERS

app = Flask(__name__)


@app.route('/hh')
def httpheaders():
    get_request()
    with open(HTTP_HEADERS_FILENAME, "r") as f:
        data = f.read()
        
    return "[" + data[:-2] + "]"


@app.route('/hhp')
def httpheaders_pretty():
    get_request()
    with open(HTTP_HEADERS_FILENAME, "r") as f:
        data = f.readlines()
        resp = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf8">
<title>HTTP Headers</title>
</head> <body>
[<BR>
"""
    for d in data:
        resp += d + "<BR>"
    resp = resp[:-6] + resp[-5:] + "]<br></body>\n</html>"
    return resp


def get_request():
    # copy of headers
    headers = Headers(request.headers)
    # remove cookie
    for h in REMOVE_HEADERS:
        if headers.has_key(h):
            headers.pop(h)
    json_headers = json.dumps(OrderedDict(headers))
    # read file
    with open(HTTP_HEADERS_FILENAME, "r") as f:
        headers_data = f.readlines()
    # append new headers
    headers_data.append(json_headers + ",\n")
    # deduplicate
    headers_data_to_write = list(OrderedDict.fromkeys(headers_data))
    
    # write output data
    with open(HTTP_HEADERS_FILENAME, "w") as f:
        for h in headers_data_to_write:
            f.write(h)
    
    return json_headers

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return get_request()


@app.route('/ip')
def ipaddr():
    get_request()
    return request.remote_addr


if __name__ == '__main__':
    app.run(debug=True)