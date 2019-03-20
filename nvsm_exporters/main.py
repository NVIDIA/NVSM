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
import json
import os
import urllib3
import subprocess
import time
import sys
import traceback
import yaml

from prometheus_client import start_http_server

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 

modules = []
prometheus_port = 8000
prometheus_exporters = []
exporters_interval = 20


if not os.path.exists("config.yml"):
    sys.exit("config.yml does not exist")

try:
    with open("config.yml") as ymlfile:
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
            traceback.print_exc()
            print "Failed"
            continue
    time.sleep(exporters_interval)
