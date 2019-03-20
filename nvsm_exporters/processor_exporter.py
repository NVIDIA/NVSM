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

ip = "localhost"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 

metric_map = {} 

coreCount = "core_count"
threadCount = "thread_count"
cpuCount = "cpu_count"

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
    if coreCount not in metric_map:
        # Create metric and add it to metric_map
        metric_map[coreCount] = Gauge(coreCount, "Total Number of Core in CPUs")
        
    if threadCount not in metric_map:
        metric_map[threadCount] = Gauge(threadCount, "Total Number of threads in CPUs")
        
    if cpuCount not in metric_map:
        metric_map[cpuCount] = Gauge(cpuCount, "Total Number of CPUs")
        
    print("Initialized Processor Exporter...")

def ExportMetric(ip="localhost", port="273"):
    
    """
    ExportMetric: This function requests from NVSM-APIs using URL. Upon gettin valid JSON data traverses the data and create and set values to metrics.
    The metrics include:
        1. Total Number of Cores in CPUs
        2. Total Number of Threads in CPUs
        3. Total Number of CPUs
        
    Args:
        ip  : IP address of the NVSM server
        port: Port  number of the NVSM server
        
    Returns:
        None
    """
    core_count = 0
    thread_count = 0
    cpu_count = 0
    
    # Read JWT token for NVSM-APIs
    with open ('/etc/nvsm-apis/nvsm-apis-perpetual.jwt', 'r') as jwt_file:
        tokenstring = jwt_file.read()

    # Request to URL to get the data
    r = requests.get('https://' + str(ip) + ':' + str(port) + '/redfish/v1/Systems/1/Processors', timeout=5, verify=False, headers={'Authorization': 'Bearer '+tokenstring})
    
    # Read data returned by URL
    data = r.json()
    
    # Iterate over the processor collection to get the processor information
    for processor in data["Members"]:
        r = requests.get('https://' + str(ip) + ':273' + processor["@odata.id"], timeout=5, verify=False, headers={'Authorization': 'Bearer '+tokenstring})
        proc_data = r.json()
        core_count += proc_data["TotalCores"]
        thread_count += proc_data["TotalThreads"]
        cpu_count += 1
        
    coreCount_metric = metric_map[coreCount]
    threadCount_metric = metric_map[threadCount]
    cpuCount_metric = metric_map[cpuCount]

    coreCount_metric.set(core_count)
    threadCount_metric.set(thread_count)
    cpuCount_metric.set(cpu_count)
