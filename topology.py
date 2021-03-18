#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import argparse

from comnetsemu.cli import CLI, spawnXtermDocker
from comnetsemu.net import Containernet, VNFManager
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.node import Controller

if __name__ == "__main__":

    # Only used for auto-testing.
    AUTOTEST_MODE = os.environ.get("COMNETSEMU_AUTOTEST_MODE", 0)

    setLogLevel("info")


    net = Containernet(controller=Controller, link=TCLink, xterms=False)
    mgr = VNFManager(net)

    info("*** Add controller\n")
    net.addController("c0")

    info("*** Creating hosts\n")
    h1 = net.addDockerHost(
        "h1", dimage="twamp", ip="10.0.0.1", docker_args={"hostname": "h1"},
    )
    h2 = net.addDockerHost(
        "h2", dimage="twamp", ip="10.0.0.2", docker_args={"hostname": "h2"},
    )

    info("*** Adding switch and links\n")
    switch1 = net.addSwitch("s1")
    switch2 = net.addSwitch("s2")
    net.addLink(switch1, h1, bw=10, delay="10ms")
    net.addLink(switch1, switch2, bw=10, delay="10ms")
    net.addLink(switch2, h2, bw=10, delay="10ms")

    info("\n*** Starting network\n")
    net.start()

    srv1 = mgr.addContainer("srv1", "h1", "twamp", "python3 /home/twampy.py sender 10.0.0.2:861", docker_args={})
    srv2 = mgr.addContainer("srv2", "h2", "twamp", "python3 /home/twampy.py responder 10.0.0.2:861", docker_args={})

    info("*** retrieving measurements, wait for 10s...")
    time.sleep(10)
    info("\nTwamp results: \n")
    print(srv1.dins.logs().decode("utf-8"))


    mgr.removeContainer("srv1")
    mgr.removeContainer("srv2")
    net.stop()
    mgr.stop()
   