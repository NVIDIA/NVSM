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

ip = "localhost"

metric_map = {} 

metric_map["status"] = -1
count = 0 

system_power_consumption = "system_power_consumption"
psu_health = "psu_health"

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
    if system_power_consumption not in metric_map:
        # Create metric and add it to metric_map
        metric_map[system_power_consumption] = Gauge(system_power_consumption, "System Power Consumption")
        
    if psu_health not in metric_map:
        metric_map[psu_health] = Gauge(psu_health, "PSU Overall Health")
        
    print("Initialized Power Exporter...")

def ExportMetric(ip="localhost", port="273"):
    
    """
    ExportMetric: This function requests from NVSM-APIs using URL. Upon gettin valid JSON data traverses the data and create and set values to metrics.
    The metrics include:
        1. System Overall Power Consumption
        2. PSU Overall Health Status
        3. Per PSU Power Consumption
        4. Per PSU Health Status
        
    Args:
        ip  : IP address of the NVSM server
        port: Port  number of the NVSM server
        
    Returns:
        None
    """
    
    count = 0
    power_usage = 0
    global metric_map
    
    # Read JWT token for NVSM-APIs
    with open ('/etc/nvsm-apis/nvsm-apis-perpetual.jwt', 'r') as jwt_file:
        tokenstring = jwt_file.read()
        
    # Request to URL to get the data
    r = requests.get('https://' + str(ip) + ':' + str(port) + '/redfish/v1/Chassis/1/Power', timeout=5, verify=False, headers={'Authorization': 'Bearer '+tokenstring})
    
    # Read data returned by URL
    data = r.json()
    
    # Iterate over the PowerSupplies collection to get the PowerSupply information
    for powersupply in data['PowerSupplies']:
        name = powersupply["Name"] 
        if name not in metric_map:
            metric_map[name] = Gauge(name, "Power Consumption")
        c = metric_map[name]
        if(powersupply["LastPowerOutputWatts"] == "na"):
            c.set(0)
        else:
            c.set(int(powersupply["LastPowerOutputWatts"]))
        
        
        h = powersupply["Status"]["Health"]
        status = metric_map["status"]

        if h == "Ok":
            temp = 0
            count += 1
        elif h == "Warning":
            temp = 1
        else:
            temp = 2
        if count >= 5:
            status = 0 
        elif status < temp:
            status = temp
        metric_map["status"] = status
        
        name = powersupply["Name"] + "_Health"
        if name not in metric_map:
            metric_map[name] = Gauge(name, "PSU Health")
        c = metric_map[name]
        c.set(temp)

        power_usage += int(powersupply["LastPowerOutputWatts"])
    
    status = metric_map["status"]
    system_power_metric = metric_map[system_power_consumption]
    health_metric = metric_map[psu_health]
    
    system_power_metric.set(power_usage)
    health_metric.set(status)
