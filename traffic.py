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
    h1 = net.addDockerHost("h1", dimage="ditg", ip="10.0.0.1", docker_args={"hostname": "h1"})
    h2 = net.addDockerHost("h2", dimage="measure", ip="10.0.0.2", docker_args={"hostname": "h2"})
    h3 = net.addDockerHost("h3", dimage="ditg", ip="10.0.0.3", docker_args={"hostname": "h3"})
    h4 = net.addDockerHost("h4", dimage="measure", ip="10.0.0.4", docker_args={"hostname": "h4"})

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
    
    ########TWAMP MEASUREMENT DIND
    for i in range(3):
        info("*** Starting traffic ...\n")
        info("*** Starting D-ITG receiver ...\n")
        #h2.cmd("./pathload_classic/pathload_snd &")
        srv3 = mgr.addContainer("srv3", "h3", "ditg", "./D-ITG/bin/ITGRecv", docker_args={})
        time.sleep(1)
        srv1 = mgr.addContainer("srv1", "h1", "ditg", "./D-ITG/bin/ITGSend -a 10.0.0.3 -C 5000 -c 415 -t 600000 -l recv_log_file", docker_args={})
        time.sleep(5)
        ret= srv1.dins.logs().decode("utf-8")
        print(f"- Retrieving measurements \n{ret}")
        info("*** Starting pathload receiver ...\n")
        srv2 = mgr.addContainer("srv2", "h2", "measure", "python3 ./twampy.py responder 10.0.0.2:861", docker_args={})
        time.sleep(1)
        info("*** starting pathload sender...\n")
        #ret= h4.cmd("timeout 5m ./pathload_classic/pathload_rcv -s 10.0.0.2 > test.txt")
        srv4 = mgr.addContainer("srv4", "h4", "measure", "python3 ./twampy.py sender 10.0.0.2:861", docker_args={})
        time.sleep(20)
        info("*** creating csv file...\n")
        ret= srv4.dins.logs().decode("utf-8")
        print(f"- Retrieving measurements \n{ret}")
        f = open("dind_traffic_9_"+str(i)+".csv", "w")
        f.write(ret)
        f.close()
        mgr.removeContainer("srv1")
        mgr.removeContainer("srv2")
        mgr.removeContainer("srv3")
        mgr.removeContainer("srv4")

    ########### TWAMP MEASUREMENT VM/HOST
    '''
    for i in range(3):
        
        info("*** Starting traffic ...\n")
        info("*** Starting D-ITG receiver ...\n")
        h3.cmd("./D-ITG/bin/ITGRecv &")
        time.sleep(1)
        h1.cmd("./D-ITG/bin/ITGSend -a 10.0.0.3 -C 5000 -c 415 -t 60000 -l recv_log_file &")
        time.sleep(5)
    
        info("*** Starting pathload receiver ...\n")
        h2.cmd("python3 ./twampy.py responder 10.0.0.2:861 &")
        time.sleep(1)
        info("*** starting pathload sender...\n")
        ret=h4.cmd("python3 ./twampy.py sender 10.0.0.2:861")
        time.sleep(20)
        info("*** creating csv file...\n")
        print(f"- Retrieving measurements \n{ret}")
        f = open("vm_traffic_9_"+str(i)+".csv", "w")
        f.write(ret)
        f.close()
    '''
    ######## PATHLOAD MEASUREMENT DIND
    '''
    for i in range(3):
        
        info("*** Starting traffic ...\n")
        info("*** Starting D-ITG receiver ...\n")
        srv3 = mgr.addContainer("srv3", "h3", "ditg", "./D-ITG/bin/ITGRecv", docker_args={})
        time.sleep(1)
        srv1 = mgr.addContainer("srv1", "h1", "ditg", "./D-ITG/bin/ITGSend -a 10.0.0.3 -C 5000 -c 300 -t 600000 -l recv_log_file", docker_args={})
        time.sleep(5)
        ret= srv1.dins.logs().decode("utf-8")
        print(f"- Retrieving measurements \n{ret}")
        
        info("*** Starting pathload receiver ...\n")
        srv2 = mgr.addContainer("srv2", "h2", "twamp", "./pathload_classic/pathload_snd &", docker_args={})
        time.sleep(1)
        info("*** starting pathload sender...\n")
        srv4 = mgr.addContainer("srv4", "h4", "twamp", "bash ./pathload_rcv.sh", docker_args={})
        time.sleep(120)
        info("*** creating csv file...\n")
        ret= srv4.dins.logs().decode("utf-8")
        print(f"- Retrieving measurements \n{ret}")
        f = open("dind_path_0_"+str(i)+".csv", "w")
        f.write(ret)
        f.close()
        #mgr.removeContainer("srv1")
        mgr.removeContainer("srv2")
        #mgr.removeContainer("srv3")
        mgr.removeContainer("srv4")
    '''

    ######## PATHLOAD MEASUREMENT VM/HOST
    '''
    for i in range(3):
        info("*** Starting traffic ...\n")
        info("*** Starting D-ITG receiver ...\n")
        h3.cmd("./D-ITG/bin/ITGRecv &")
        time.sleep(1)
        h1.cmd("./D-ITG/bin/ITGSend -a 10.0.0.3 -C 5000 -c 415 -t 60000 -l recv_log_file &")
        time.sleep(5)

        info("*** Starting pathload receiver ...\n")
        h2.cmd("./pathload_classic/pathload_snd &")
        time.sleep(1)
        info("*** starting pathload sender...\n")
        ret=h4.cmd("bash ./pathload_rcv.sh")
        time.sleep(20)
        info("*** creating csv file...\n")
        print(f"- Retrieving measurements \n{ret}")
        f = open("vm_path_9_"+str(i)+".csv", "w")
        f.write(ret)
        f.close()
    '''

    net.stop()
    mgr.stop()
