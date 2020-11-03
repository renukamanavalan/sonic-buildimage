#!/usr/bin/env bash


# Container image version
# Acquires build image version as its version during build
#
IMAGE_VERSION="0.0.0"

if [ "${RUNTIME_OWNER}" == "" ]; then
    RUNTIME_OWNER="kube"
fi

/usr/share/sonic/scripts/container_state.py up -f snmp -o ${RUNTIME_OWNER} -v ${IMAGE_VERSION}

mkdir -p /etc/ssw /etc/snmp

SONIC_CFGGEN_ARGS=" \
    -d \
    -y /etc/sonic/sonic_version.yml \
    -t /usr/share/sonic/templates/sysDescription.j2,/etc/ssw/sysDescription \
    -y /etc/sonic/snmp.yml \
    -t /usr/share/sonic/templates/snmpd.conf.j2,/etc/snmp/snmpd.conf \
"

sonic-cfggen $SONIC_CFGGEN_ARGS

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" > /var/sonic/config_status
