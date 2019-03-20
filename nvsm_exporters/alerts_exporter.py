#!/usr/bin/env python
#
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.


from prometheus_client import Gauge
import requests
import time
import urllib3
import traceback
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 

metric_map = {}

alerts_count = "alerts_count"

def init():
    if alerts_count not in metric_map:
        metric_map[alerts_count] = Gauge(alerts_count, "Number of Alerts")
        print("Initialized Alert Exporter...")

def ExportMetric(ip="localhost", port="273"):
    alerts = 0
    with open ('/etc/nvsm-apis/nvsm-apis-perpetual.jwt', 'r') as jwt_file:
        tokenstring = jwt_file.read()

    r = requests.get('https://' + str(ip) + ':' + str(port) + '/nvsm/v1/Chassis/1/Alerts', timeout=120, verify=False, headers={'Authorization': 'Bearer '+tokenstring})

    alerts_collection = r.json()

    if alerts_collection["MemberCount"] !=0:
        for alert in alerts_collection["Alerts"]:
            if alert["state"] != "cleared" and alert["severity"] == "1":
                alerts += 1

    r = requests.get('https://' + str(ip) + ':' + str(port) + '/nvsm/v1/Systems/1/Alerts', timeout=120, verify=False, headers={'Authorization': 'Bearer '+tokenstring})

    alerts_collection = r.json()

    if alerts_collection["MemberCount"] !=0:
        for alert in alerts_collection["Alerts"]:
            if alert["state"] != "cleared" and alert["severity"] == "1":
                alerts += 1
                
    alert_metric = metric_map[alerts_count]
    alert_metric.set(alerts)
