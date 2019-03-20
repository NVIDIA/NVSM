#!/usr/bin/env python
#
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from prometheus_client import Gauge, Summary, Counter
import requests
import time
import urllib3
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 

metric_map = {}

correctable = "correctable_memory_errors"
uncorrectable = "uncorrectable_memory_errors"
dimm_count = "dimm_count"
dimm_health = "dimm_health"

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
    if correctable not in metric_map:
        # Create metric and add it to metric_map
        metric_map[correctable] = Gauge(correctable, "Correctable Memory Errors")
        
    if uncorrectable not in metric_map:
        metric_map[uncorrectable] = Gauge(uncorrectable, "Uncorrectable Memory Errors")
        
    if dimm_count not in metric_map:
        metric_map[dimm_count] = Gauge(dimm_count, "Number of DIMMs")
        
    if dimm_health not in metric_map:
            metric_map[dimm_health] = Gauge(dimm_health, "DIMM Health")
            
    print("Initialized Memory Exporter...")

def ExportMetric(ip="localhost", port="273"):
    
    """
    ExportMetric: This function requests from NVSM-APIs using URL. Upon gettin valid JSON data traverses the data and create and set values to metrics.
    The metrics include:
        1. Correctable Memory Errors
        2. Uncorrectable Memory Errors
        3. Number of DIMMs
        
    Args:
        ip  : IP address of the NVSM server
        port: Port  number of the NVSM server
        
    Returns:
        None
    """
    
    global metric_map
    dimms = 0
    
    with open ('/etc/nvsm-apis/nvsm-apis-perpetual.jwt', 'r') as jwt_file:
        tokenstring = jwt_file.read()

    r = requests.get('https://' + str(ip) + ':' + str(port) + '/redfish/v1/Systems/1/Memory', timeout=5, verify=False, headers={'Authorization': 'Bearer '+tokenstring})
        
    data = r.json()

    correctable_total = 0
    uncorrectable_total = 0

    for data_id,val in enumerate(data["Members"]):
        r = requests.get('https://' + str(ip) + ':' + str(port) + val["@odata.id"], timeout=5, verify=False, headers={'Authorization': 'Bearer '+tokenstring})
        data_cpu = r.json()

        dimms += 1

        correctable_total += int(data_cpu["Oem"]["Error"]["CorrectableCount"])
        uncorrectable_total += int(data_cpu["Oem"]["Error"]["UncorrectableCount"])

        name = data_cpu["Id"] + "_capacity"
        if name not in metric_map:
            metric_map[name] = Gauge(name, "DIMM Capacity")
        c = metric_map[name]
        cap = (float(data_cpu["CapacityMiB"])) 
        c.set(cap)

        h = data_cpu["Status"]["Health"]
        health_metric = metric_map[dimm_health]
            
        status = 2
        if(h  == "OK"):
            status = 0
        elif(h == "Warning"):
            status = 1

        health_metric.set(status)

    correctable_metric = metric_map[correctable]
    uncorrectable_metric = metric_map[uncorrectable]
    count_metric = metric_map[dimm_count]

    count_metric.set(dimms)
    correctable_metric.set(correctable_total)
    uncorrectable_metric.set(uncorrectable_total)
