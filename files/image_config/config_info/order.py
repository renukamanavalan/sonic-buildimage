#! /usr/bin/env python

import os
import sys
import json
import argparse
import collections


global tables, groups, services
global ordered_diff, restart_services

tables = {}
groups = {}
services = {}

ordered_diff = []
restart_services = set()

def err_exit(msg):
    print(msg)
    exit(-1)


def update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            d[k] = update(d.get(k, type(v)()), v)
        else:
            d[k] = v
    return d

def parse_config(cfg_file):
    global tables, groups, services

    d = {}
    with open(cfg_file, "r") as s:
        d = json.load(s)

    if 'tables' not in d or 'groups' not in d or 'services' not in d:
        err_exit("Expect tables, groups & services in config file: Present: {}".format(d.keys()))

    tables = d["tables"]
    groups = d["groups"]
    services = d["services"]

 

def order_tables(inp):
    global ordered_diff, restart_services

    coll = {}

    for t in inp:
        if t in tables:
            grp_name = tables[t]["order_group"] if t in tables else "unknown"
            grp = groups[grp_name] if grp_name in groups else sys.maxint
            index = tables[t]["order_index"] if t in tables else sys.maxint
            restart_services.update(tables[t]["services_to_restart"])
        else:
            grp = sys.maxint
            index = sys.maxint

        e = { grp: { index: { t: inp[t] } } }

        coll = update(coll, e)

        # print("collection:")
        # print(json.dumps(coll, indent=4))
        # print("-" * 40)


    grps = coll.keys()
    grps.sort()

    for g in grps:
        entry = coll[g]
        indices = entry.keys()
        indices.sort()

        for i in indices:
            ordered_diff.append(coll[g][i])

    svcs = restart_services.copy()
    for s in svcs:
        if s in services and s in restart_services:
            for r in services[s]['auto_restart']:
                restart_services.discard(r)


    print("Services order")
    print(json.dumps(ordered_diff, indent=4))
    print("*" * 40)
    print("")

    print("services collected: {}".format(str(svcs)))
    print("")

    print("services to restart:")
    for s in restart_services:
        warm_mode = "not-available"
        dataplane_impact = False
        if s in services:
            if "warm_reboot" in services[s] and services[s]["warm_reboot"] == "true":
                warm_mode = "enabled"

            if "dataplane_impact" in services[s] and services[s]["dataplane_impact"] == "true":
                dataplane_impact = True

        print("    {} warm_reboot:{} data-plane: {}".format(s, warm_mode, dataplane_impact))

    print("*" * 40)
    print("")


def main():
    parser=argparse.ArgumentParser(description="Analyze diff")
    parser.add_argument("-j", "--json", help="JSON diff to analyze")
    parser.add_argument("-c", "--config", help="COnfig required")
    args = parser.parse_args()

    parse_config(args.config)
    
    with open(args.json, "r") as s:
        order_tables(json.load(s))

    print("END")

if __name__ == "__main__":
    main()

