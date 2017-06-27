# standard libs
import os
import json
import sys
import base64

# 3th party libs
from flask import Flask
from flask import request

from trident import logger
log = logger.getLogger()
from trident import handler

app = Flask(__name__)


@app.route("/")
def index():
    env = os.environ.items
    log.debug("in index. %s" % env)

    return json.dumps("Trident is the demo app to ingest time series data to Predix TimeSeries database<br/><br/>\
                      Access https://github.com/pxie/trident.git for more info.")


@app.route("/test", methods=['GET'])
def test():
    log.debug("in /test")
    handler.test_ingestion()

    return "test"

if __name__ == "__main__":

    if os.getenv("PORT"):
        port = int(os.getenv("PORT"))
    else:
        port = 5050

    app.run(host='0.0.0.0', port=port)
