import os
import sys
import pdb
import random
import pickle
from itertools import islice
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.util import dumpNodeConnections
from mininet.link import TCLink
from mininet.node import OVSController
from mininet.node import Controller
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.util import quietRun
import random
from subprocess import Popen, PIPE
from time import sleep, time
from ripl.ripl.dctopo import JellyfishTopo, FatTreeTopo

def InitTestJf(numberSwitch, numberPorts,adjListFile, flowsNumber, routeringmode):
	jelly_topo = JellyfishTopo(numberSwitch, numberPorts, adjListFile)
	randomHosts = jelly_topo.hosts()
	random.shuffle(randomHosts)
	clients = randomHosts[0::2]
	servers = randomHosts[1::2]
	pairs_list = zip(clients, servers)

	#fileName = 'mn_script_ecmp_' + str(flowsNumber) +'_eight_flows'
	fileName = routeringmode + 'scriptJf'
	file = open(fileName, 'w')
	
	for pair in pairs_list:
		#print pair[1] + " iperf -s &"
		#print pair[0] + " iperf -c %s -P 8 -t 60 >> 'results/ecmp_8_eight_output.txt &" %(pair[1])
		file.write(str(pair[1]) + " iperf -s & \n")
		file.write(str(pair[0]) + ' iperf -c ' + str(pair[1]) + ' -P ' + str(flowsNumber) + ' -t 10' + ' >> results/'+ routeringmode + '/' + str(pair[0]) +'__' + pair[1] + '.txt' + ' &\n')
	file.close()

	fileName2 = 'iperfkill'
	file2 = open(fileName2,'w')
	for pair in pairs_list:
		file2.write(str(pair[1]) + " sudo pkill iperf & \n")
	file2.close()


def InitTestFt(pods, routeringmode, flowsNumber):
	fat_topo = FatTreeTopo(pods)
	randomHosts = fat_topo.hosts()
 	random.shuffle(randomHosts)
 	clients = randomHosts[0::2]
 	servers = randomHosts[1::2]
 	pairs_list = zip(clients, servers)

 	#fileName = 'mn_script_ecmp_' + str(flowsNumber) +'_eight_flows'
 	fileName = routeringmode + 'scriptFt'
 	file = open(fileName, 'w')
	
 	for pair in pairs_list:
 		#print pair[1] + " iperf -s &"
 		#print pair[0] + " iperf -c %s -P 8 -t 60 >> 'results/ecmp_8_eight_output.txt &" %(pair[1])
 		file.write(str(pair[1]) + " iperf -s & \n")
 		file.write(str(pair[0]) + ' iperf -c ' + str(pair[1]) + ' -P ' + str(flowsNumber) + ' -t 10' + ' >> results/'+ routeringmode + '/' + str(pair[0]) +'__' + pair[1] + '.txt' + ' &\n')
 	file.close()

 	fileName2 = 'iperfkill'
	file2 = open(fileName2,'w')
	for pair in pairs_list:
		file2.write(str(pair[1]) + " sudo pkill iperf & \n")
	file2.close()



	#Utilizando grafo:	
# def InitTestFt(hosts, flowsNumber, routeringmode):
# 	randomHosts = hosts
# 	random.shuffle(randomHosts)
# 	clients = randomHosts[0::2]
# 	servers = randomHosts[1::2]
# 	pairs_list = zip(clients, servers)

# 	#fileName = 'mn_script_ecmp_' + str(flowsNumber) +'_eight_flows'
# 	fileName = routeringmode + 'scriptFt'
# 	file = open(fileName, 'w')
	
# 	for pair in pairs_list:
# 		#print pair[1] + " iperf -s &"
# 		#print pair[0] + " iperf -c %s -P 8 -t 60 >> 'results/ecmp_8_eight_output.txt &" %(pair[1])
# 		file.write(str(pair[1]) + " iperf -s & \n")
# 		file.write(str(pair[0]) + ' iperf -c ' + str(pair[1]) + ' -P ' + str(flowsNumber) + ' -t 10' + ' >> results/'+ routeringmode + '/' + str(pair[0]) +'__' + pair[1] + '.txt' + ' &\n')
# 	file.close()


