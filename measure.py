#!/usr/bin/python

import sys
import os
import time
import argparse
from plot import *



from comnetsemu.cli import CLI, spawnXtermDocker
from comnetsemu.net import Containernet, VNFManager
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.node import Controller
from mininet.topo import Topo
from mininet.net import Mininet
from comnetsemu.node import APPContainer, DockerHost


#########################################
def customTopoChain(num): # fixed number of switches, related to number of hosts
    
    '''
    Topo: Chain topology  h1     h2     h3         hn
                            |      |      |          |
                            s1 --- s2 --- s3 --- ... sn
    '''

    info("*** Adding Docker hosts and switches in a chain topology\n")
    last_sw = None
    hosts = list()
    for i in range(num):
        host = net.addDockerHost(
            "h%s" % (i + 1),
            dimage="measure",
            ip="10.0.0.%s" % (i + 1),
            docker_args={"hostname": "h%s" % (i + 1)},
        )
        hosts.append(host)
        switch = net.addSwitch("s%s" % (i + 1))
        net.addLink(switch, host, bw=10, delay="10ms")
        if last_sw:
            # Connect switches
            net.addLink(switch, last_sw, bw=10, delay="10ms")
        last_sw = switch


def customTopoTree(depth=1, fanout=2 ):
    
    '''
    Topo: Tree topology    h1 \\
                                s2 \\
                           h2 //    \\
                                     s1
                           h3 \\    //
                                s3 //
                           hn //
    '''

    hostNum = 1
    switchNum = 1
    addTree(depth, fanout, hostNum, switchNum)
  
    
def addTree(depth, fanout, hostNum, switchNum):
    isSwitch = depth > 0
    if isSwitch:
        node = net.addSwitch( 's%s' % switchNum )
        switchNum += 1
        for _ in range( fanout ):
            l = addTree( depth - 1, fanout, hostNum , switchNum )
            child = l[0]
            hostNum = l[1]
            switchNum = l[2]
            net.addLink( node, child,  bw=10, delay='10ms' )
    else:
        node = net.addDockerHost( 'h%s' % hostNum,
                                    dimage="measure",
                                    ip="10.0.0.%s" % hostNum,
                                    docker_args={"hostname": "h%s" % hostNum})
        hostNum += 1
        
    return [node,hostNum,switchNum]


def customTopoDumbbell(num):  # fixed number of switches (2)
    
    '''
    Topo: Dumbbell topology  hn/2 --- s1 --- s2 --- hn/2
                        
    '''

    hosts = list()
    for i in range(num):
        host = net.addDockerHost(
            "h%s" % (i + 1),
            dimage="measure",
            ip="10.0.0.%s" % (i + 1),
            docker_args={"hostname": "h%s" % (i + 1)},
        )
        hosts.append(host)
    info("*** Adding switches and links\n")
    s1 = net.addSwitch( 's1' )
    s2 = net.addSwitch( 's2' )
    net.addLink( s1, s2, bw=10, delay='10ms' )
    for x in hosts[:num//2]:
        net.addLink( x, s1, bw=10, delay='10ms' )
    for x in hosts[num//2:]:
        net.addLink( x, s2, bw=10, delay='10ms' )     

###################################################################

###ArgumentParser

# Initialize parser
parser = argparse.ArgumentParser(
    prog='measure.py',
    formatter_class=argparse.RawDescriptionHelpFormatter)
# Adding arguments
parser.add_argument("-snd", help = "Set sender address", required=True)
parser.add_argument("-rcv", help = "Set receiver address", required=True)
parser.add_argument("-topo", help = "Select topology from proposed ones: [tree][chain][dumbbell]", required=True)
# Read arguments from command line
args = parser.parse_args()

snd = args.snd
rcv = args.rcv
topo = args.topo

#####

def customTopo(topo):
    if(topo == "tree"):
        print("tree selected")
        depth = int(input ("Insert depth of the tree: "))
        fanout = int(input ("Insert fanout of the tree: "))

        customTopoTree(depth,fanout)

    elif(topo == "chain"):
        print("chain selected")
        n = int(input ("Insert number of hosts: "))

        customTopoChain(n)

    elif(topo == "dumbbell"):
        print("dumbbell selected")
        n = int(input ("Insert number of hosts: "))

        customTopoDumbbell(n)

    else:
        print("Topology not found")    

def runPathload(snd,rcv):

    for i in range(3):
        info("*** Starting pathload sender at "+ snd +"...\n")
        srv_snd = mgr.addContainer("srv_snd", "h"+ snd[-1], "measure", "./pathload_classic/pathload_snd &", docker_args={})
        time.sleep(5)
        info("*** starting pathload receiver at "+ rcv +"...\n")

        srv_rcv = mgr.addContainer("srv_rcv", "h"+ rcv[-1], "measure", "bash ./pathload_rcv.sh "+ snd, docker_args={}) 
        time.sleep(300)

        info("*** creating csv file...\n")
        ret= srv_rcv.dins.logs().decode("utf-8")
        print(f"- Retrieving measurements \n{ret}")
        f = open("path_"+str(i)+".csv", "w")
        f.write(ret)
        
        f.close()
        mgr.removeContainer("srv_snd")
        mgr.removeContainer("srv_rcv")


def runTwamp(snd,rcv):
    
    for i in range(3):
        info("*** Starting twamp receiver at "+ rcv+ "...\n")
        srv_rcv = mgr.addContainer("srv_rcv", "h"+ rcv[-1], "measure", "python3 ./twampy.py responder "+ rcv +":861", docker_args={})
        time.sleep(1)
        
        info("*** starting twamp sender at "+ snd +"...\n")
        srv_snd = mgr.addContainer("srv_snd", "h"+ snd[-1], "measure", "python3 ./twampy.py sender "+ rcv +":861", docker_args={})
        time.sleep(30)
        
        info("*** creating csv file...\n")
        ret= srv_snd.dins.logs().decode("utf-8")
        print(f"- Retrieving measurements \n{ret}")
        f = open("tw_"+str(i)+".csv", "w")
        f.write(ret)
        f.close()
        
        mgr.removeContainer("srv_rcv")
        mgr.removeContainer("srv_snd")


def launch(snd, rcv):
    runTwamp(snd, rcv)
    runPathload(snd, rcv)
   

if __name__ == "__main__":

    setLogLevel("info")

    net = Containernet(controller=Controller, link=TCLink, xterms=False)
    mgr = VNFManager(net)

    info("*** Add controller\n")
    net.addController("c0")

    customTopo(topo)

    info("\n*** Starting network\n") 
    net.start()

    launch(snd, rcv)
    plot_results()

    net.stop()
    mgr.stop()