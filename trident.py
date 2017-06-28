# standard libs
import os
import json
import sys
import base64

# 3th party libs
from flask import Flask
from flask import make_response, request

from trident import logger
log = logger.getLogger()
from trident import handler

app = Flask(__name__)


@app.route("/")
def index():
    env = os.environ.items
    log.debug("in index. %s" % env)

    return json.dumps("<h2>Intro</h2><br/>\
                        Trident is the demo app to ingest time series data to Predix TimeSeries database<br/><br/>\
                        Access <b>https://github.com/pxie/trident.git</b> for more info.")


@app.route("/test", methods=['GET'])
def test():
    log.debug("in /test")
    success, msg = handler.test()
    if success:
        status = 200
    else:
        status = 500

    return make_response(msg, status)


@app.route("/ingest", methods=['GET'])
def ingest():
    log.debug("in /ingest")
    return handler.ingest()

if __name__ == "__main__":

    if os.getenv("PORT"):
        port = int(os.getenv("PORT"))
    else:
        port = 5050

    app.run(host='0.0.0.0', port=port)
