import json
import os
import os.path
from collections import OrderedDict

from flask import Flask, request, render_template
from werkzeug.datastructures import Headers

from settings import HTTP_HEADERS_FILENAME, REMOVE_HEADERS

app = Flask(__name__)


def dedup(data):
    return list(OrderedDict.fromkeys(data))


@app.route('/hh')
def httpheaders():
    get_request()
    if request.args.get("pretty") is None:
        with open(os.path.abspath(HTTP_HEADERS_FILENAME), "r") as f:
            data = f.read()
        return "[" + data[:-2] + "]"
    else:
        with open(os.path.abspath(HTTP_HEADERS_FILENAME), "r") as f:
            data = f.readlines()
        # remove last colon
        data[-1] = data[-1][:-2]
        return render_template("headers.html", headers=data)


def get_request():
    # copy of headers
    headers = Headers(request.headers)
    # remove unwanted extra headers
    for h in REMOVE_HEADERS:
        if headers.has_key(h):
            headers.pop(h)
    json_headers = json.dumps(OrderedDict(headers))
    # create file if not exists
    if not os.path.isfile(os.path.abspath(HTTP_HEADERS_FILENAME)):
        with open(os.path.abspath(HTTP_HEADERS_FILENAME), "w+"):
            pass

    # read file
    with open(os.path.abspath(HTTP_HEADERS_FILENAME), "r") as f:
        headers_data = f.readlines()
    # append new headers
    headers_data.append(json_headers + ",\n")
    # deduplicate
    headers_data_to_write = dedup(headers_data)

    # write output data
    with open(os.path.abspath(HTTP_HEADERS_FILENAME), "w") as f:
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
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']  # if behind a proxy


@app.route('/ua')
def ua():
    get_request()
    headers = request.headers
    if "User-Agent" in headers:
        return headers["User-Agent"]
    else:
        return ""


@app.route('/uagents')
def uagents():
    get_request()
    with open(HTTP_HEADERS_FILENAME, "r") as f:
        headers_data = f.read()
    # remove colon
    headers_data = headers_data[:-2]
    uagents = list()
    json_headers = json.loads("[" + headers_data + "]")
    for h in json_headers:
        if "User-Agent" in h:
            uagents.append(h["User-Agent"])
    uagents = dedup(uagents)
    arg = request.args.get("pretty")
    if arg is None:
        return json.dumps(uagents)
    else:
        return render_template("uagents.html", uagents=uagents)


@app.route('/help')
def helpinfo():
    get_request()
    return render_template("help.html")


if __name__ == '__main__':
    app.run(debug=True)
