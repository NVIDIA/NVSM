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
prometheus_port = 8000
prometheus_exporters = []
exporters_interval = 20
DefaultConfigDir = "/etc/nvsm-apis/"
DefaultConfigFile = "nvsm-prometheus-exporters.config"
DefaultConfigFilePath = DefaultConfigDir + DefaultConfigFile

if not os.path.exists(DefaultConfigFilePath):
    sys.exit("Config file does not exist")

try:
    with open(DefaultConfigFilePath) as ymlfile:
        configyml = yaml.load(ymlfile)
except:
    sys.exit("Error in config file")

if "prometheus" in configyml:
    prometheus_port = int(configyml['prometheus']['port'])
    prometheus_exporters = configyml['prometheus']['exporters']
    exporters_interval = configyml['prometheus']['interval']

start_http_server(prometheus_port)

for e in prometheus_exporters:
    mod = e.replace(".py", "")
    #importlib.import_module(mod)
    module = __import__(mod)
    module.init()
    modules.append(module)
    
while(True):
    for module in modules:
        ExportMetric = getattr(module, 'ExportMetric')
        try:
            ExportMetric()
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print e
            print "Failed"
            continue
    time.sleep(exporters_interval)
