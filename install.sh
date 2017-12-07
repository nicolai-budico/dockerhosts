#!/bin/sh

set -e

if [ $(id --user) -ne 0 ] ; then
    echo "Superuser priveleges required"
    exit 1
fi

WORKDIR="$(dirname "$(readlink -f "${0}")")"

echo "Install file /etc/systemd/system/dockerhosts.service"
cp "${WORKDIR}/dockerhosts.service" "/etc/systemd/system/"

echo "Install file /usr/bin/dockerhosts"
cp "${WORKDIR}/dockerhosts.py" "/usr/bin/dockerhosts"


systemctl daemon-reload

echo "Enable service: systemctl enable dockerhosts"
systemctl enable dockerhosts

echo "Starting service: systemctl start dockerhosts"
systemctl start dockerhosts

systemctl status dockerhosts
