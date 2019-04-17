#!/usr/bin/env python
#
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import importlib
import os
import urllib3
import time
import sys
import yaml
import alerts_exporter
import gpu_exporter
import memory_exporter
import pcie_exporter
import processor_exporter
import storage_exporter
import thermal_exporter
import power_exporter

from prometheus_client import start_http_server

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 

modules = []
metric_exporter_port = 8000
metric_exporters = []
nvsm_host = "localhost"
nvsm_port = 273
exporters_interval = 20
DefaultConfigDir = "/etc/nvsm-apis/"
DefaultConfigFile = "nvsm-prometheus-exporters.config"
DefaultConfigFilePath = DefaultConfigDir + DefaultConfigFile

# Check if config file exists
if not os.path.exists(DefaultConfigFilePath):
    sys.exit("Config file does not exist")

# Open config file
try:
    with open(DefaultConfigFilePath) as ymlfile:
        configyml = yaml.load(ymlfile)
except:
    sys.exit("Error in config file")

# Check if config file contains metric_exporter info
if "metric_exporter" in configyml:
    metric_exporter_port = int(configyml['metric_exporter']['port'])
    metric_exporters = configyml['metric_exporter']['exporters']
    exporters_interval = configyml['metric_exporter']['interval']
else:
    sys.exit("Error in config file")

# Check if config file contains NVSM info
if "nvsm" in configyml:
    nvsm_host = configyml['nvsm']['host']
    nvsm_port = int(configyml['nvsm']['port'])

# Start http_server for metric exporters
start_http_server(metric_exporter_port)

# Import all the modules and call the init functions for each one of them
for e in metric_exporters:
    mod = e.replace(".py", "")
    module = __import__(mod)
    module.init()
    modules.append(module)
    
# Run the exporters at exporters_interval intervals
while(True):
    for module in modules:
        ExportMetric = getattr(module, 'ExportMetric')
        try:
            ExportMetric(nvsm_host, nvsm_port)
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print e
            print "Failed"
            continue
    time.sleep(exporters_interval)
