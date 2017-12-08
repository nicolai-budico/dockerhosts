### Dev

Tested on Kubuntu 17.10 only

### About

This tool is a linux service that provides DNS for docker containers. You may reach your containers by hostname, e.g.

```
$ docker run -d --hostname=myapp.local.com --rm -it ubuntu:17.10
9af0b6a89feee747151007214b4e24b8ec7c9b2858badff6d584110bed45b740

$ nslookup myapp.local.com
Server:         127.0.0.53
Address:        127.0.0.53#53

Non-authoritative answer:
Name:   myapp.local.com
Address: 172.17.0.2

$ ping myapp.local.com
PING myapp.local.com (172.17.0.2) 56(84) bytes of data.
64 bytes from myapp.local.com (172.17.0.2): icmp_seq=1 ttl=64 time=0.150 ms

$ docker stop 9af0b6a89feee747151007214b4e24b8ec7c9b2858badff6d584110bed45b740
9af0b6a89feee747151007214b4e24b8ec7c9b2858badff6d584110bed45b740

$ nslookup myapp.local.com
Server:         127.0.0.53
Address:        127.0.0.53#53

** server can't find myapp.local.com: NXDOMAIN

$ ping myapp.local.com
ping: myapp.local.com: Name or service not known
```

### Requirements

1. Python 3
2. Dnsmasq
3. Docker

### Install
```
sudo ./install.sh
```

This command will install `dockerhosts` service.

### Uninstall
```
sudo ./uninstall.sh
```

This command will remove `dockerhosts` service and all associated files


### Configuration

This tool uses `dnsmasq` to provide associations between container hosnames and theirs IP addresses.
By default dnsmasq listens on 127.0.0.54:53, to make this DNS available in the system (tested Kubuntu 17.10 only) 
add IP 127.0.0.54 in property `DNS` in file `/etc/systemd/resolved.conf`:
```
cat /etc/systemd/resolved.conf
#  This file is part of systemd.
#
#  systemd is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2.1 of the License, or
#  (at your option) any later version.
#
# Entries in this file show the compile time defaults.
# You can change settings by editing this file.
# Defaults can be restored by simply deleting this file.
#
# See resolved.conf(5) for details

[Resolve]
DNS=127.0.0.54
#FallbackDNS=
#Domains=
#LLMNR=yes
#MulticastDNS=yes
#DNSSEC=no
#Cache=yes
#DNSStubListener=udp
```
