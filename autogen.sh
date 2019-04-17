#!/bin/sh

# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.


mkdir -p config m4
autoreconf --force --install -I config -I m4
#autoreconf --force --install
if [ $? -eq 0 ]; then
    echo "Ready to run configure"
    echo "eg.: ./configure --sysconfdir=/etc --localstatedir=/var"
else
    echo "FAILED!"
fi

