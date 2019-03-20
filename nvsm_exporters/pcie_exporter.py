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

correctable = "PCIE_correctable_errors"
uncorrectable = "PCIE_uncorrectable_errors"

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
        metric_map[correctable] = Gauge(correctable, "Correctable PCIe Errors")
        
    if uncorrectable not in metric_map:
        metric_map[uncorrectable] = Gauge(uncorrectable, "Uncorrectable PCIe Errors")
        
    print("Initialized PCIe Exporter...")

def ExportMetric(ip="localhost", port="273"):
    
    """
    ExportMetric: This function requests from NVSM-APIs using URL. Upon gettin valid JSON data traverses the data and create and set values to metrics.
    The metrics include:
        1. Correctable PCIe Errors
        2. Uncorrectable PCIe Errors
        
    Args:
        ip  : IP address of the NVSM server
        port: Port  number of the NVSM server
        
    Returns:
        None
    """
    
    # Read JWT token for NVSM-APIs
    with open ('/etc/nvsm-apis/nvsm-apis-perpetual.jwt', 'r') as jwt_file:
        tokenstring = jwt_file.read()

    # Request to URL to get the data
    r = requests.get('https://' + str(ip) + ':' + str(port) + '/nvsm/v1/Systems/1/Pcie/Errors', timeout=120, verify=False, headers={'Authorization': 'Bearer '+tokenstring})

    # Read data returned by URL
    data = r.json()
    
    correctable_metric = metric_map[correctable]
    uncorrectable_metric = metric_map[uncorrectable]
    
    correctable_metric.set(int(data["Correctable"]["ErrorCount"]))
    uncorrectable_metric.set(int(data["Uncorrectable"]["ErrorCount"]))

