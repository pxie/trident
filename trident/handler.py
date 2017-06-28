from trident import logger
log = logger.getLogger()

import os
import json
import requests
import uuid
import websocket
import time
from multiprocessing import Process
import queue
import threading
import random


def test():
    token = get_access_token()

    # build ingestion request
    env = get_env()
    url = env["predix-timeseries"][0]["credentials"]["ingest"]["uri"]
    headers = {"Authorization": "Bearer " + token,
               "predix-zone-id": env["predix-timeseries"][0]["credentials"]["ingest"]["zone-http-header-value"],
               "Origin": "http://predix.io"}

    ws = get_ws_conn()
    # build ingestion message
    messageID = str(uuid.uuid4())
    timestamp = int(round(time.time() * 1000))
    payload = {
        "messageId": messageID,
        "body": [
            {
                "name": "Temp5217-3437",
                "datapoints": [
                    [timestamp - 500, 90.3, 2],
                    [timestamp, 100, 3]
                ],
                "attributes": {
                    "maint": "2017-03-21",
                    "location": "sh-factory-01"
                }
            }
        ]
    }
    return ingest_data(url, headers, payload)


def insert_queue():
    q = queue.Queue()
    jobs = 50
    now = int(round(time.time() * 1000))    # millionseconds
    two_years_before = now - 2 * 365 * 24 * 60 * 60 * 1000
    step = int(2 * 365 * 24 * 60 * 60 * 1000 / jobs)

    for item in range(jobs):
        log.debug("insert item: %s to queue.",
                  (item, two_years_before + step * item))
        q.put((item, two_years_before + step * item))

    log.debug("queue size: %d", q.qsize())

    return q


def get_ws_conn():
    token = get_access_token()

    # build ingestion request
    env = get_env()
    url = env["predix-timeseries"][0]["credentials"]["ingest"]["uri"]
    headers = {"Authorization": "Bearer " + token,
               "predix-zone-id": env["predix-timeseries"][0]["credentials"]["ingest"]["zone-http-header-value"],
               "Origin": "http://predix.io"}
    ws = websocket.WebSocket()
    ws.connect(url, header=headers)

    return ws


def do_ingest():
    q = insert_queue()

    threads = []
    num_worker_threads = 2
    now = time.time()
    for i in range(num_worker_threads):
        ws = get_ws_conn()
        t = threading.Thread(target=worker, args=(ws, q))
        t.start()
        threads.append(t)

    q.join()
    for i in range(num_worker_threads):
        q.put(None)
    for t in threads:
        t.join()

    duration = round(time.time() - now)
    log.debug("it is finished to ingest 50,000 data points. it took %ds", duration)


def worker(ws, q):
    while True:
        item = q.get()
        if item is None:
            break
        send_data(ws, item)
        q.task_done()
    ws.close()


def build_message(item):
    log.debug("build message. get item: %s", item)
    index, start_timestamp = item

    message_size = 1         # each message size contains 1000 data points
    two_years = 2 * 365 * 24 * 60 * 60 * 1000  # millionseconds
    jobs = 50
    step = int(two_years / jobs / message_size)

    data_points = []
    for i in range(message_size):
        data_points.append([start_timestamp + step * i,
                            calc_datapoint(index), random.randint(0, 3)])
    log.debug("message data points: %s", data_points)
    messageId = str(uuid.uuid4())
    message = {
        "messageId": messageId,
        "body": [
            {
                "name": "Temp5217-3437",
                "datapoints": data_points
            }
        ]
    }

    return message


def calc_datapoint(index):
    # TODO: enhance formula later
    return random.random()


def send_data(ws, item):
    message = build_message(item)

    log.debug("Sending data: %s", message)
    ws.send(json.dumps(message))

    log.debug("Receiving...")
    result = ws.recv()
    log.debug("Received '%s'" % result)


def ingest():
    # async ingest 500,000 data points in last 2 years
    p = Process(target=do_ingest)
    p.start()

    return "<h2>Notice</h2><br/>\
            This task is started to async ingest 500,000 data points in last 2 years<br>\
            Please run <b>'cf logs trident‘</b> to check whether task is finished."


def ingest_data(url, headers, payload):
    ws = websocket.WebSocket()
    ws.connect(url, header=headers)

    log.debug("Sending data: %s", payload)
    ws.send(json.dumps(payload))
    log.debug("Sent")

    log.debug("Receiving...")
    result = ws.recv()
    log.debug("Received '%s'" % result)
    ws.close()

    data = json.loads(result)
    if data["statusCode"] == 202 and data["messageId"] == payload["messageId"]:
        ret = (True, "<h2>successfully ingest data.</h2>")
    else:
        ret = (False,
               "<h2>fail to ingest data, please run 'cf logs trident --recent' for more info.</h2>")

    return ret


def load_config():
    log.debug(os.getcwd())
    with open('config.json') as data_file:
        config = json.load(data_file)
    log.debug(config)

    return config


def get_access_token():
    config = load_config()
    env = get_env()

    body = {'grant_type': 'client_credentials', 'client_id': config["uaa"]["clientid"],
            'client_secret': config["uaa"]["clientsecret"], 'response_type': 'token'}
    uaa = env["predix-uaa"][0]["credentials"]["issuerId"]

    log.debug("in get_access_token. body: %s, url: %s", body, uaa)

    response = requests.post(uaa, data=body)
    token = response.json()['access_token']

    return token


def get_env():
    if os.getenv("VCAP_SERVICES"):
        data = os.getenv("VCAP_SERVICES")
    else:
        data = """{
            "predix-timeseries": [
            {
                "credentials": {
                "ingest": {
                "uri": "wss://gateway-predix-data-services.run.aws-jp01-pr.ice.predix.io/v1/stream/messages",
                "zone-http-header-name": "Predix-Zone-Id",
                "zone-http-header-value": "b8143253-2b36-4187-adac-e28dfecc5a3b",
                "zone-token-scopes": [
                "timeseries.zones.b8143253-2b36-4187-adac-e28dfecc5a3b.user",
                "timeseries.zones.b8143253-2b36-4187-adac-e28dfecc5a3b.ingest"
                ]
                },
                "query": {
                "uri": "https://time-series-store-predix.run.aws-jp01-pr.ice.predix.io/v1/datapoints",
                "zone-http-header-name": "Predix-Zone-Id",
                "zone-http-header-value": "b8143253-2b36-4187-adac-e28dfecc5a3b",
                "zone-token-scopes": [
                "timeseries.zones.b8143253-2b36-4187-adac-e28dfecc5a3b.user",
                "timeseries.zones.b8143253-2b36-4187-adac-e28dfecc5a3b.query"
                ]
                }
                },
                "label": "predix-timeseries",
                "name": "demo-ts",
                "plan": "Free",
                "provider": null,
                "syslog_drain_url": null,
                "tags": [
                "timeseries",
                "time-series",
                "time series"
                ],
                "volume_mounts": []
            }
            ],
            "predix-uaa": [
            {
                "credentials": {
                "dashboardUrl": "https://uaa-dashboard.run.aws-jp01-pr.ice.predix.io/#/login/12ad48d8-5e0a-4d29-9165-35a628e368c9",
                "issuerId": "https://12ad48d8-5e0a-4d29-9165-35a628e368c9.predix-uaa.run.aws-jp01-pr.ice.predix.io/oauth/token",
                "subdomain": "12ad48d8-5e0a-4d29-9165-35a628e368c9",
                "uri": "https://12ad48d8-5e0a-4d29-9165-35a628e368c9.predix-uaa.run.aws-jp01-pr.ice.predix.io",
                "zone": {
                "http-header-name": "X-Identity-Zone-Id",
                "http-header-value": "12ad48d8-5e0a-4d29-9165-35a628e368c9"
                }
                },
                "label": "predix-uaa",
                "name": "demo-uaa",
                "plan": "Free",
                "provider": null,
                "syslog_drain_url": null,
                "tags": [],
                "volume_mounts": []
            }
            ]
            }
        """
    log.debug("get env. dir: %s, type: %s" % (dir(data), type(data)))
    env = json.loads(data)
    log.debug(env)

    return env

if __name__ == "__main__":

    ws = get_ws_conn()
    item = (1, int(round(time.time() * 1000)))
    send_data(ws, item)
