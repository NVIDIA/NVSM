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

    """
    Init function to initialize the module,
    Initialize Prometheus metrics that would be later used in the module

    Args:
        None

    Returns:
        None

    """

    # Check if metric already present in the metric_map
    if alerts_count not in metric_map:
        
        # Create metric and add it to metric_map
        metric_map[alerts_count] = Gauge(alerts_count, "Number of Alerts")

        print("Initialized Alert Exporter...")

def ExportMetric(ip="localhost", port="273"):
    """
    ExportMetric: This function requests from NVSM-APIs using URL. Upon gettin valid JSON data traverses the data and create and set values to metrics.
    The metrics include:
        1. Number of Alerts
        
    Args:
        ip  : IP address of the NVSM server
        port: Port  number of the NVSM server
        
    Returns:
        None
    """

    alerts = 0

    # Read JWT token for NVSM-APIs
    with open ('/etc/nvsm-apis/nvsm-apis-perpetual.jwt', 'r') as jwt_file:
        tokenstring = jwt_file.read()

    # Request to URL to get the data
    r = requests.get('https://' + str(ip) + ':' + str(port) + '/nvsm/v1/Chassis/1/Alerts', timeout=120, verify=False, headers={'Authorization': 'Bearer '+tokenstring})

    # Read data returned by URL
    alerts_collection = r.json()

    # Check the MemberCount, state of alert and severity of alert
    if alerts_collection["MemberCount"] !=0:
        for alert in alerts_collection["Alerts"]:
            if alert["state"] != "cleared" and alert["severity"] == "1":

                # Increment count of alerts
                alerts += 1

    # Request to URL to get the data
    r = requests.get('https://' + str(ip) + ':' + str(port) + '/nvsm/v1/Systems/1/Alerts', timeout=120, verify=False, headers={'Authorization': 'Bearer '+tokenstring})

    # Read data returned by URL
    alerts_collection = r.json()

    # Check the MemberCount, state of alert and severity of alert
    if alerts_collection["MemberCount"] !=0:
        for alert in alerts_collection["Alerts"]:
            if alert["state"] != "cleared" and alert["severity"] == "1":

                # Increment count of alerts
                alerts += 1
    
    # Set data to metrics
    alert_metric = metric_map[alerts_count]
    alert_metric.set(alerts)
