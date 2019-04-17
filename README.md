# NVSM-Prometheus

This project contains prometheus exporters using NVSM
## Cloning

Use the following command to clone the repository:

```
git clone https://gitlab-master.nvidia.com/dgx/nvsm/nvsm-prometheus.git
```

## Building

### Prerequisites

On systems running Ubuntu 16.04 and above, the following commands must be run prior
to building to install all the required packages:

```
$ sudo apt-get update
$ sudo apt-get install autoconf python-pip
$ pip install pyinstaller
```
### Building debian

Use following commands to build the debian package, this assumes that user is already in the root folder of the cloned project:

```
$ ./autogen.sh
$ ./configure --sysconfdir=/etc --localstatedir=/var
$ make debian
```
