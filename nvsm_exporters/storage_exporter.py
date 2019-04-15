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
created = False


metric_map["status"] = -1

os_ssd_count = "os_count"
data_ssd_count = "data_count"
health = "drive_health"
avg_data = "avg_data_used"
avg_os = "avg_os_used"



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
    if os_ssd_count not in metric_map:
        # Create metric and add it to metric_map
        metric_map[os_ssd_count] = Gauge(os_ssd_count, "Number of OS Drives")
        
    if data_ssd_count not in metric_map:
        metric_map[data_ssd_count] = Gauge(data_ssd_count, "Number of Data Drives")
        
    if health not in metric_map:
        metric_map[health] = Gauge(health, "Drive Health")
        
    if avg_data not in metric_map:
        metric_map[avg_data] = Gauge(avg_data, "Average Percent used Data Drives")
        
    if avg_os not in metric_map:
        metric_map[avg_os] = Gauge(avg_os, "Average Percent Used OS Drives")
        
    print("Initialized Storage Exporter...")


def ExportMetric(ip="localhost", port= "273"):
    """
    ExportMetric: This function requests from NVSM-APIs using URL. Upon gettin valid JSON data traverses the data and create and set values to metrics.
    The metrics include:
        1. Number of OS Drives
        2. Number of Data Drives
        3. Overall Drive Health
        4. Average Percent used for Data Drives
        5. Average Percent use for OS Drives
        6. Per Drive Disk Capacity
        7. Per Drive Percent Used
        
    Args:
        ip  : IP address of the NVSM server
        port: Port  number of the NVSM server
        
    Returns:
        None
    """
    
    global metric_map
    
    avg_os_used = 0
    avg_data_used = 0
    os_count = 0
    data_count = 0
    
    # Read JWT token for NVSM-APIs
    with open ('/etc/nvsm-apis/nvsm-apis-perpetual.jwt', 'r') as jwt_file:
        tokenstring = jwt_file.read()

    # Request to URL to get the data
    r = requests.get('https://' + str(ip) + ':' + str(port) + '/redfish/v1/Systems/1/Storage', timeout=120, verify=False, headers={'Authorization': 'Bearer '+tokenstring})
    
    # Read data returned by URL
    storage_collection = r.json()

    # Iterate over the storage collection to get the storage information
    for data_id in storage_collection["Members"]:
        
        # Request to URL to get the data
        r = requests.get('https://' + str(ip) + ':' + str(port) + '/' + data_id["@odata.id"], timeout=120, verify=False, headers={'Authorization': 'Bearer '+tokenstring})

        # Read data returned by URL
        try:
            nvme_storage_subsys = r.json()
        except:
            continue
        
        # Iterate over the storage information to get the drive information
        for nvme_id in nvme_storage_subsys["Drives"]:
            
            # Request to URL to get the data for each drive
            r = requests.get('https://' + str(ip) + ':' + str(port) +nvme_id["@odata.id"], timeout=120, verify=False, headers={'Authorization': 'Bearer '+tokenstring})
            
            try:
                drive = r.json()
            except:
                continue
            
            if "nvme0n1" in drive["@odata.id"] or "nvme1n1" in drive["@odata.id"]:
                name =  "os_" + drive["@odata.id"][-7:] + "_capacity"
            else:
                name = "data_" + drive["@odata.id"][-7:] + "_capacity"
            if name not in metric_map:
                metric_map[name] = Gauge(name, "Disk Capacity")
            c = metric_map[name]
            c.set(float(drive["Capacity"]))

            if "nvme0n1" in drive["@odata.id"] or "nvme1n1" in drive["@odata.id"]:
                usage_name =  "os_" + drive["@odata.id"][-7:] + "_percent_used"
                avg_os_used += float(drive["Oem"]["Nvidia_HM"]["Metrics"]["PercentUsed"])
            else:
                usage_name =  "data_" + drive["@odata.id"][-7:] + "_percent_used" 
                avg_data_used += float(drive["Oem"]["Nvidia_HM"]["Metrics"]["PercentUsed"])
            if usage_name not in metric_map:
                metric_map[usage_name] = Gauge(usage_name, "Percent Used")
            g = metric_map[usage_name]
            g.set(float(drive["Oem"]["Nvidia_HM"]["Metrics"]["PercentUsed"])) 

            if "nvme0n1" in drive["@odata.id"] or "nvme1n1" in drive["@odata.id"]:
                error_name =  "os_" + drive["@odata.id"][-7:] + "_media_errors"
            else:
                error_name =  "data_" + drive["@odata.id"][-7:] + "_media_errors"
            if error_name not in metric_map:
                metric_map[error_name] = Gauge(error_name, "Media Errors")
            d = metric_map[error_name]
            d.set(int(drive["Oem"]["Nvidia_HM"]["Errors"]["Media"]["Count"]))
        
            h = drive["Status"]["Health"] 
        
            if "nvme0n1" in drive["@odata.id"] or "nvme1n1" in drive["@odata.id"]:
                os_count += 1
            else:
                data_count += 1
            status = metric_map["status"]
            if(h == "OK"):
                temp = 0
            elif(h == "Warning"):
                temp = 1
            elif(h == "Critical"):
                temp = 2
            if(status < temp):
                status = temp
                metric_map["status"] =  status
    
    # Set values to metrics
    status = metric_map["status"]
    health_metric = metric_map[health]
    health_metric.set(status)
    
    os_ssd_count_metric = metric_map[os_ssd_count]
    os_ssd_count_metric.set(os_count)
    
    data_ssd_count_metric = metric_map[data_ssd_count]
    data_ssd_count_metric.set(data_count)
    
    avg_os_metric = metric_map[avg_os]
    avg_os_metric.set(avg_os_used/os_count)
    
    avg_data_metric = metric_map[avg_data]
    avg_data_metric.set(avg_data_used/data_count)
