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
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 

metric_map = {} 
metric_map["fan_status"] = -1
metric_map["temp_status"] = -1 

temp_health = "temperature_health"
fan_health = "fan_health"

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
    if temp_health not in metric_map: 
        # Create metric and add it to metric_map
        metric_map[temp_health] = Gauge(temp_health, "Temperature Overall Health") 
    
    # Check if metric already present in the metric_map
    if fan_health not in metric_map:
        # Create metric and add it to metric_map
        metric_map[fan_health] = Gauge(fan_health, "Fan Overall Health")
        
    print("Initialized Thermal Exporter...")

def ExportMetric(ip="localhost", port="273"):
    """
    ExportMetric: This function requests from NVSM-APIs using URL. Upon gettin valid JSON data traverses the data and create and set values to metrics.
    The metrics include:
        1. PDB Temperature Reading
        2. PDB Temperature Overall Health Status
        3. Per PDB Temperature Health Status
        4. Fan Speeds
        5. Fan Overall Health Status
        6. Per Fan Health Status
        
    Args:
        ip  : IP address of the NVSM server
        port: Port  number of the NVSM server
        
    Returns:
        None
    """
    
    global metric_map
    
    # Read JWT token for NVSM-APIs
    with open ('/etc/nvsm-apis/nvsm-apis-perpetual.jwt', 'r') as jwt_file:
        tokenstring = jwt_file.read()

    # Request to URL to get the data
    r = requests.get('https://' + str(ip) + ':' + str(port) + '/redfish/v1/Chassis/1/Thermal', timeout=5, verify=False, headers={'Authorization': 'Bearer '+tokenstring})

    # Read data returned by URL
    data = r.json()
    
    # Iterate over the temperature sensors to create metrics and set values to the metrics
    for temperatures in data['Temperatures']:
        temp_name = str(temperatures["Name"]).split()[0]
        name = temp_name +  "_temp"
        if name not in metric_map:
            metric_map[name] = Gauge(name, "PDB Temperature")
        c = metric_map[name]
        c.set(temperatures["ReadingCelsius"])
        
        h = temperatures["Status"]["Health"] 
         

        status = metric_map["temp_status"]
        if(h == "OK"):
            temp = 0
        elif(h == "Warning"):
            temp = 1
        elif(h == "Critical"):
            temp = 2
        if(status < temp):
            status = temp
            metric_map["temp_status"] = status
        
        name = temp_name +  "_status"
        if name not in metric_map:
            metric_map[name] = Gauge(name, "PDB Health Status")
        c = metric_map[name]
        c.set(temp)

    # Iterate over fan sensors to create metrics and set values to the metrics
    for fans in data["Fans"]:
        name = fans["Name"] + "_speed"
        if name not in metric_map:
            metric_map[name] = Gauge(name, "Fan Speed")
        c = metric_map[name]
        c.set(fans["Reading"])

        h = fans["Status"]["Health"]
        name = fans["Name"] + "_health"
        if name not in metric_map:
            metric_map[name] = Gauge(name, "Fan Health Status")
        c = metric_map[name]
        

        status = metric_map["fan_status"]
        if(h == "OK"):
            temp = 0
        elif(h == "Warning"):
            temp = 1
        else:
            temp = 2
        if(status < temp):
            status = temp
            metric_map["fan_status"] = status
        c.set(temp)

    # Set values to metrics
    temp_health_metric = metric_map[temp_health]
    fan_health_metric = metric_map[fan_health]
    
    status = metric_map["temp_status"]
    temp_health_metric.set(status)
    
    status = metric_map["fan_status"]
    fan_health_metric.set(status)
