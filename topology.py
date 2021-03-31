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


    setLogLevel("info")


    net = Containernet(controller=Controller, link=TCLink, xterms=False)
    mgr = VNFManager(net)

    info("*** Add controller\n")
    net.addController("c0")

    info("*** Creating hosts\n")
    h1 = net.addDockerHost("h1", dimage="twamp", ip="10.0.0.1", docker_args={"hostname": "h1"})
    h2 = net.addDockerHost("h2", dimage="twamp", ip="10.0.0.2", docker_args={"hostname": "h2"})
    h3 = net.addDockerHost("h3", dimage="twamp", ip="10.0.0.3", docker_args={"hostname": "h3"})
    h4 = net.addDockerHost("h4", dimage="twamp", ip="10.0.0.4", docker_args={"hostname": "h4"})

    info("*** Adding switch and links\n")
    switch1 = net.addSwitch("s1")
    switch2 = net.addSwitch("s2")
    net.addLink(switch1, h1, bw=10, delay="10ms")
    net.addLink(switch1, h2, bw=10, delay="10ms")
    net.addLink(switch1, switch2, bw=10, delay="10ms")
    net.addLink(switch2, h3, bw=10, delay="10ms")
    net.addLink(switch2, h4, bw=10, delay="10ms")

    info("\n*** Starting network\n")
    net.start()

    info("*** First block of measurements without traffic...\n")
    # Run twamp responder
    srv3 = mgr.addContainer("srv3", "h3", "twamp", "python3 /home/twampy.py responder 10.0.0.3:861", docker_args={})
    # Wait twamp responder to start.
    time.sleep(1)

    ret = h1.cmd("python3 /home/twampy.py sender 10.0.0.3:861")
    print(f"- Retrieving first twamp mesurements: \n{ret}")
    ret = h1.cmd("python3 /home/twampy.py sender 10.0.0.3:861")
    print(f"- Retrieving second twamp mesurements: \n{ret}")

    info("*** Second block of measurements with traffic...\n")
    # Run iperf3 server
    srv2 = mgr.addContainer("srv2", "h2", "twamp", "iperf3 -s", docker_args={})
    # Wait iperf3 server to start.
    time.sleep(1)
    
    print(f"-Sending udp stream for 50 seconds with 10mb/s to h2 (approx 60MB total)\n")
    ret = h4.cmd("iperf3 -c 10.0.0.2 -u -t 50 -b 10m &") #60MB tot
    ret = h1.cmd("python3 /home/twampy.py sender 10.0.0.3:861")
    print(f"- Retrieving first twamp mesurements: \n{ret}")
    
    ret3 = h1.cmd("python3 /home/twampy.py sender 10.0.0.3:861")
    print(f"- Retrieving second twamp mesurements: \n{ret3}")



    '''
    #For manual testing with bash

    srv1 = mgr.addContainer("srv1", "h1", "twamp", "python3 /home/twampy.py sender 10.0.0.3:861", docker_args={})
    srv2 = mgr.addContainer("srv2", "h2", "twamp", "iperf3 -c 10.0.0.4 -u -t 20 -b 10m", docker_args={})
    srv3 = mgr.addContainer("srv3", "h3", "twamp", "python3 /home/twampy.py responder 10.0.0.3:861", docker_args={})
    srv4 = mgr.addContainer("srv4", "h4", "twamp", "iperf3 -s", docker_args={})
    
  
    srv1 = mgr.addContainer("srv1", "h1", "twamp", "bash", docker_args={})
    srv2 = mgr.addContainer("srv2", "h2", "twamp", "bash", docker_args={})
    srv3 = mgr.addContainer("srv3", "h3", "twamp", "bash", docker_args={})
    srv4 = mgr.addContainer("srv4", "h4", "twamp", "bash", docker_args={})
    

    spawnXtermDocker("srv1")
    spawnXtermDocker("srv2")
    spawnXtermDocker("srv3")
    spawnXtermDocker("srv4")
    CLI(net)
    
    info("*** generating traffic...")
    time.sleep(10)
    print(srv2.dins.logs().decode("utf-8"))

    info("*** retrieving twamp measurements...")
    time.sleep(20)
    info("\nTwamp results: \n")
    print(srv1.dins.logs().decode("utf-8"))
    '''

    #mgr.removeContainer("srv1")
    mgr.removeContainer("srv2")
    mgr.removeContainer("srv3")
    #mgr.removeContainer("srv4")
    net.stop()
    mgr.stop()
   