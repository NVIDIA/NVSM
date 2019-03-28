# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

sbin_PROGRAMS = nvsm_prometheus_exporters

nvsm_prometheus_exporters_SOURCES =  alerts_exporter.py \
				     gpu_exporter.py \
				     main.py \
				     memory_exporter.py \
				     pcie_exporter.py \
				     power_exporter.py \
			             processor_exporter.py \
			             storage_exporter.py \
				     thermal_exporter.py

systemddir = $(libdir)/systemd/system
dist_systemd_DATA = nvsm-prometheus-exporters.service

configdir = $(sysconfdir)/nvsm-apis
dist_config_DATA = \
	nvsm-prometheus-exporters.config

nvsm_prometheus_exporters$(EXEEXT): $(nvsm_prometheus_exporters_SOURCES)
	pyinstaller --onefile main.py
	mv dist/main nvsm_prometheus_exporters
