#!/usr/bin/env python
#
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.


from prometheus_client import start_http_server
from prometheus_client import Gauge, Summary, Counter
from prometheus_client.core import GaugeMetricFamily, REGISTRY
import requests
import time 
import urllib3
import sys
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 

metric_map = {}

health_created = False
created = False

gpu_count = "GPU_count"
gpu_healthrollup = "gpu_healthrollup"

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
    if gpu_count not in metric_map: 

        # Create metric and add it to metric_map
        metric_map[gpu_count] = Gauge(gpu_count, "Number of GPUs")

    if not created:
        metric_map[gpu_healthrollup] = Gauge(gpu_healthrollup, "GPU HealthRollup")

        print("Initialized GPU Exporter...")

def ExportMetric(ip="localhost", port="273"):
    """
    ExportMetric: This function requests from NVSM-APIs using URL. Upon gettin valid JSON data traverses the data and create and set values to metrics.
    The metrics include:
        1. Number of GPUs   - gpu_count
        2. GPU HealthrollUp - gpu_healthrollup
        3. Per GPU PCIe link width 
        4. Per GPU PCIe link generation
        5. Per GPU Health
        6. Per GPU Retired Pages

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
    r = requests.get('https://' + str(ip) + ':' + str(port) + '/nvsm/v1/Systems/1/GPUs', verify=False, timeout=10, headers={'Authorization': 'Bearer '+tokenstring})

    # Read data returned by URL
    data = r.json()

    # Set GPU count metric
    c = metric_map[gpu_count]
    c.set(int(data["Members@odata.count"]))

    health_endpoint = data["Health"]["@odata.id"]
        
    time.sleep(5)

    # Request to URL to get the data
    r = requests.get('https://' + str(ip) + ':' + str(port) + health_endpoint, verify=False, timeout=10, headers={'Authorization': 'Bearer '+tokenstring})

    # Read data returned by URL
    health_data = r.json()

    health = health_data["Health"]
    status = 2

    if health == "Ok":
        status = 0
    elif health == "Warning":
        status = 1

    # Set GPU healthrollup metric
    healthrollup_metric = metric_map[gpu_healthrollup]
    healthrollup_metric.set(status)

    for gpu_endpoint in data["Members"]:
        time.sleep(5)

        # Request to URL to get the data
        r = requests.get('https://' + str(ip) + ':' + str(port) + gpu_endpoint["@odata.id"], verify=False, timeout=10, headers={'Authorization': 'Bearer '+tokenstring})

        # Read data returned by URL
        gpu = r.json()
        
        # Create Per GPU pcie link width metric
        name = "pcie_link_width_" + str(gpu["Inventory"]["UUID"])
        name = name.replace('-','_')
        if name not in metric_map:
            metric_map[name] = Gauge(name, "PCIe Link Width")
        c = metric_map[name]
        c.set(int(gpu["Connections"]["PCIeLinkWidth"][:-1]))

        # Create Per GPU pcie link gen info metric
        name = "pcie_link_gen_info_" + str(gpu["Inventory"]["UUID"])
        name = name.replace('-','_')
        if name not in metric_map:
            metric_map[name] = Gauge(name, "PCIe Generation Info")
        c = metric_map[name]
        c.set(int(gpu["Connections"]["PCIeGen"]))

        h = gpu["Status"]["Health"]
        
        # Create Per GPU health metric
        name = "gpu_health_" + str(gpu["Inventory"]["UUID"])
        name = name.replace('-','_')
        if name not in metric_map:
            metric_map[name] = Gauge(name, "Per GPU Health")
        c = metric_map[name]
        if(h == "OK"):
            staus = 0
        elif(h == "Warning"):
            status = 1
        elif(h == "Critical"):
            status = 2
        c.set(status)

        # Create Per GPU retired pages metric
        name = "retired_pages_" + str(gpu["Inventory"]["UUID"])
        name = name.replace('-','_')
        if name not in metric_map:
            metric_map[name] = Gauge(name, "Per GPU Retired Pages")
        c = metric_map[name]
        single_bit_errors = int(gpu["Stats"]["ErrorStats"]["RetiredPages"]["DueToMultipleSingleBitErrors"]["PageCount"])
        double_bit_errors = int(gpu["Stats"]["ErrorStats"]["RetiredPages"]["DueToDoubleBitErrors"]["PageCount"])
        pending_retirement = int(gpu["Stats"]["ErrorStats"]["RetiredPages"]["PendingRetirementCount"])
        c.set(single_bit_errors + double_bit_errors + pending_retirement )
