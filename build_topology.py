# encoding: utf-8
import os
import sys
import networkx
import matplotlib as mpl
import random
mpl.use('Agg')
import matplotlib.pyplot as plt
import pickle
from itertools import islice
from jelly_utils import *
from netaddr import EUI, mac_unix, IPAddress
import argparse

def compute_ecmp_pathsFT(networkx_graph, n):
	ecmp_paths = {}
	#print(networkx.drawing.nx_agraph.to_agraph(networkx_graph))
	for a in range(n):
		for b in range(a+1, n):
			shortest_paths = networkx.all_shortest_paths(networkx_graph, str(a+1), str(b))

			ecmp_paths[(str(a), str(b))] = [p for p in shortest_paths]
	return ecmp_paths

def compute_ecmp_paths(networkx_graph, n):
	ecmp_paths = {}
	#print(networkx.drawing.nx_agraph.to_agraph(networkx_graph))
	for a in range(n):
		for b in range(a+1, n):
			shortest_paths = networkx.all_shortest_paths(networkx_graph, source=str(a), target=str(b))
			ecmp_paths[(str(a), str(b))] = [p for p in shortest_paths]
	return ecmp_paths

def compute_k_shortest_pathsFT(networkx_graph, n, k=8):
	all_ksp = {}
	for a in range(n):
	    for b in range(a+1, n):
		ksp = list(islice(networkx.shortest_simple_paths(networkx_graph, str(a+1), target= str(b)), k))
		all_ksp[(str(a), str(b))] = ksp
	return all_ksp

def compute_k_shortest_paths(networkx_graph, n, k=8):
	all_ksp = {}
	for a in range(n):
	    for b in range(a+1, n):
		ksp = list(islice(networkx.shortest_simple_paths(networkx_graph, source=str(a),	target=str(b)), k))
		all_ksp[(str(a), str(b))] = ksp
	return all_ksp





def get_path_counts(ecmp_paths, all_ksp, traffic_matrix, all_links):
	counts = {}
	# initialize counts for all links
	for link in all_links:
	    a, b = link
	    counts[(str(a),str(b))] = {"8-ksp":0, "8-ecmp": 0, "64-ecmp": 0} 
	    counts[(str(b),str(a))] = {"8-ksp":0, "8-ecmp": 0, "64-ecmp": 0} 
	for start_host in range(len(traffic_matrix)):
		dest_host = traffic_matrix[start_host]
		start_node = start_host/3
		dest_node = dest_host/3
		if start_node == dest_node:
		    continue
		# swap them so that start_node < dest_node
		if start_node > dest_node:
			start_node, dest_node = dest_node, start_node
		paths = ecmp_paths[(str(start_node), str(dest_node))]
		if len(paths) > 64:
		    paths = paths[:64]
		for i in range(len(paths)):
			path = paths[i]
			prev_node = None
			for node in path:
			    if not prev_node:
				prev_node = node
				continue
			    link = (str(prev_node), str(node))
			    if i < 8:
				counts[link]["8-ecmp"] += 1
			    counts[link]["64-ecmp"] += 1
			    prev_node = node

		ksp = all_ksp[(str(start_node), str(dest_node))]
		for path in ksp:
		    prev_node = None
		    for node in path:
			if not prev_node:
                            prev_node = node
                            continue
                        link = (str(prev_node), str(node))
			counts[link]["8-ksp"] += 1
			prev_node = node
	
	return counts


def assemble_histogram(path_counts, file_name):
	ksp_distinct_paths_counts = []
	ecmp_8_distinct_paths_counts = []
	ecmp_64_distinct_paths_counts = []
	

	for _, value in sorted(path_counts.iteritems(), key=lambda (k,v): (v["8-ksp"],k)):
	    ksp_distinct_paths_counts.append(value["8-ksp"])
	for _, value in sorted(path_counts.iteritems(), key=lambda (k,v): (v["8-ecmp"],k)):
	    ecmp_8_distinct_paths_counts.append(value["8-ecmp"])
	for _, value in sorted(path_counts.iteritems(), key=lambda (k,v): (v["64-ecmp"],k)):
	    ecmp_64_distinct_paths_counts.append(value["64-ecmp"])

#	print ksp_distinct_paths_counts
#	print ecmp_8_distinct_paths_counts
#	print ecmp_64_distinct_paths_counts
	x = range(len(ksp_distinct_paths_counts))
	fig = plt.figure()
	ax1 = fig.add_subplot(111)

	ax1.plot(x, ksp_distinct_paths_counts, color='b', label="8 Shortest Paths")
	ax1.plot(x, ecmp_64_distinct_paths_counts, color='r', label="64-way ECMP")
	ax1.plot(x, ecmp_8_distinct_paths_counts, color='g', label="8-way ECMP")
	plt.legend(loc="upper left");
	ax1.set_xlabel("Rank of Link")
	ax1.set_ylabel("# of Distinct Paths Link is on")
	file_name = 'Figura 9'
	plt.savefig("plots/%s_plot.png" % file_name)

	
	    
def save_obj(obj, name):
    with open('pickled_routes/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open('pickled_routes/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

# Code adapted from:
# https://stackoverflow.com/questions/25200220/generate-a-random-derangement-of-a-list
def random_derangement(n):
    while True:
        v = range(n)
        for j in range(n - 1, -1, -1):
            p = random.randint(0, j)
            if v[p] == j:
                break
            else:
                v[j], v[p] = v[p], v[j]
        else:
            if v[0] != 0:
                return tuple(v)

def initJfTopo(numberSwitch, inter_switch_Links,numHosts):
	
	n = numberSwitch
	numHosts = numHosts
	d = inter_switch_Links
	reuse_old_result = False
	ecmp_paths = {}
	all_ksp = {}
	file_name = "rrg_%s_%s" % (d, n)
	if not reuse_old_result:
		graph = networkx.random_regular_graph(d, n) # d = degree; n = nodes
		networkx.write_adjlist(graph, file_name)
		graph = networkx.read_adjlist(file_name)

		print "Rotas ECMP sendo criadas..."
		ecmp_paths = compute_ecmp_paths(graph, n)
		#print("ECMP PATCH")
		#print(ecmp_paths)
		save_obj(ecmp_paths, "ecmp_%s" % (file_name))
		print "Rotas KSP sendo criadas..."
		all_ksp = compute_k_shortest_paths(graph, n)
		#print("KSP PATCH")
		#print(all_ksp)
		save_obj(all_ksp, "ksp_%s" % (file_name))
	else:
		graph = networkx.read_adjlist(file_name)
		ecmp_paths = load_obj("ecmp_%s" % (file_name))
		all_ksp = load_obj("ksp_%s" % (file_name))
	#print "Assembling counts from paths"

	derangement = random_derangement(numHosts)	
	all_links = graph.edges()

	path_counts = get_path_counts(ecmp_paths, all_ksp, derangement, all_links)
	#print "Making the plot"
	assemble_histogram(path_counts=path_counts, file_name=file_name)
	
	#print "Transforming routes for Ripl/Riplpox use"
	#print "Transforming KSP"
	transformed_ksp_routes = transform_paths_dpid("ksp_%s" % (file_name), n, 8)
	save_routing_table(transformed_ksp_routes, "ksp_%s" % (file_name))
	#print "Transforming ECMP 8"
	transformed_ecmp_routes = transform_paths_dpid("ecmp_%s" % (file_name), n, 8)
	#print(transformed_ecmp_routes)
	save_routing_table(transformed_ecmp_routes, "ecmp_8_%s" % (file_name))
	
def mk_topoFt(pods):
    num_hosts         = (pods ** 3)/4
    num_agg_switches  = pods * pods
    num_core_switches = (pods * pods)/4

    hosts = [('h' + str(i))
             for i in range (1, num_hosts + 1)]

    # core_switches = [('s' + str(i))
    #                    for i in range(1,num_core_switches + 1)]

    # agg_switches = [('s' + str(i))
    #                 for i in range(num_core_switches + 1,num_core_switches + num_agg_switches+ 1)]

#Comentei a criação e ligação dos hosts e alterei nome dos switches

    core_switches = [(str(i))
                       for i in range(1,num_core_switches + 1)]

    agg_switches = [(str(i))
                    for i in range(num_core_switches + 1,num_core_switches + num_agg_switches+ 1)]


    g = networkx.Graph()
    #g.add_nodes_from(hosts)
    g.add_nodes_from(core_switches)
    g.add_nodes_from(agg_switches)

    host_offset = 0
    for pod in range(pods):
        core_offset = 0
        for sw in range(pods/2):
            switch = agg_switches[(pod*pods) + sw]

            # Connect to core switches
            for port in range(pods/2):
                core_switch = core_switches[core_offset]
                g.add_edge(switch,core_switch)
                #g.add_edge(core_switch,switch)
                core_offset += 1

            # Connect to aggregate switches in same pod
            for port in range(pods/2,pods):
                lower_switch = agg_switches[(pod*pods) + port]
                g.add_edge(switch,lower_switch)
                #g.add_edge(lower_switch,switch)

        # for sw in range(pods/2,pods):
        #     switch = agg_switches[(pod*pods) + sw]
        #     # Connect to hosts
        #     for port in range(pods/2,pods): # First k/2 pods connect to upper layer
        #         host = hosts[host_offset]
        #         # All hosts connect on port 0                
        #         g.add_edge(switch,host)
        #         #print('CONECTA SWITCH ' + switch + 'ao host ' + host)
        #         #g.add_edge(host,switch)
        #         host_offset += 1

    plt.subplot(111)
    networkx.draw_networkx(g)
    plt.savefig('GRAFO.png')
    return g



def initFtTopo(pods):
	n = pods * pods + (pods * pods)/4 #numberSwitch
	numHosts = (pods ** 3)/4
	reuse_old_result = False
	ecmp_paths = {}
	all_ksp = {}
	file_name = 'graphFt'

	if not reuse_old_result:
		graph = mk_topoFt(pods)
		networkx.write_adjlist(graph, file_name)
		graph = networkx.read_adjlist(file_name)

		plt.subplot(111)
		networkx.draw_networkx(graph)
		plt.savefig('GRAFO2.png')

		print "Rotas ECMP sendo criadas..."
		ecmp_paths = compute_ecmp_pathsFT(graph, n)
		raw_input("Press Enter to continue...")

		save_obj(ecmp_paths, "ecmp_%s" % (file_name))
		print "Rotas KSP sendo criadas..."
		all_ksp = compute_k_shortest_pathsFT(graph, n)
		save_obj(all_ksp, "ksp_%s" % (file_name))
	else:
		graph = networkx.read_adjlist(file_name)
		ecmp_paths = load_obj("ecmp_%s" % (file_name))
		all_ksp = load_obj("ksp_%s" % (file_name))

	derangement = random_derangement(numHosts)	
	all_links = graph.edges()

	path_counts = get_path_counts(ecmp_paths, all_ksp, derangement, all_links)
	#print "Making the plot"
	assemble_histogram(path_counts=path_counts, file_name=file_name)
	
	#print "Transforming routes for Ripl/Riplpox use"
	#print "Transforming KSP"
	transformed_ksp_routes = transform_paths_dpid("ksp_%s" % (file_name), n, 8)
	save_routing_table(transformed_ksp_routes, "ksp_%s" % (file_name))
	#print "Transforming ECMP 8"
	transformed_ecmp_routes = transform_paths_dpid("ecmp_%s" % (file_name), n, 8)
	save_routing_table(transformed_ecmp_routes, "ecmp_8_%s" % (file_name))

	return graph

	

