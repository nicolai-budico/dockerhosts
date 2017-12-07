#!/bin/sh

set -e

if [ $(id --user) -ne 0 ] ; then
    echo "Superuser priveleges required"
    exit 1
fi

if ( systemctl status dockerhosts 1>/dev/null 2>&1 ) ; then
    systemctl stop dockerhosts
    echo "Stop service"
else
    echo "Service is not running"
fi

if ( systemctl disable dockerhosts 2>/dev/null ) ; then
    echo "Service disabled"
else
    echo "Service is not registered"
fi

if [ -f "/etc/systemd/system/dockerhosts.service" ] ; then
    echo "Uninstall file /etc/systemd/system/dockerhosts.service"
    rm "/etc/systemd/system/dockerhosts.service"
fi

if [ -f "/usr/bin/dockerhosts" ] ; then
    echo "Uninstall file /usr/bin/dockerhosts"
    rm "/usr/bin/dockerhosts"
fi

systemctl daemon-reload

echo "Done."
