# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request

from keepass_http.core import logging
from keepass_http.httpd import requests

log = logging.getLogger(__name__)


app = Flask(__name__)


@app.route('/', methods=['POST'])
def handle():
    request_type = request.json["RequestType"]
    log.info("Got request: %s" % request_type)

    req_map = {"test-associate": requests.TestAssociateRequest(),
               "associate": requests.AssociateRequest(),
               "get-logins": requests.GetLoginsRequest(),
               "set-login": requests.SetLoginRequest(),
               "get-logins-count": requests.GetLoginsCountRequest()}

    response = req_map[request_type](request.json)
    log.info("Request was successfull: %s" % response.get("Success", "unknown??"))
    return jsonify(response)
