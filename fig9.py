# encoding: utf-8
import sys
import os
import build_topology

def reproduzFig9():
	numberSwitch = 230
	numberPorts = 10
	inter_switch_Links = 10 #degree
	flowsNumber = 8
	numHosts = 3*numberSwitch	
	# Build Topology
	build_topology.initJfTopo(numberSwitch, inter_switch_Links,numHosts) # Cria topoogia Jellyfish e rotas usando ecmp e ksp
	os.system('clear')
	print("Fig 9 foi reproduzida e encontra-se no diretório 'plots'.")

def deleteFiles():
	#Delete Results and stop mininet
	os.system('sudo rm -rf results/ecmp_8_/* results/ksp_/* pickled_routes/* transformed_routes/*')
	os.system('clear')
		
def start():
	print('Mininet sendo reiniciado...')
	os.system('sudo mn -c')
	os.system('clear')

	deleteFiles()
	print("Programa iniciado")
	reproduzFig9()
	raw_input("Pressione Enter para sair.")
	#deleteFiles()







if __name__ == "__main__":
	start()
	# for i in range(len(processList)):
	# 	processList[i].kill()


