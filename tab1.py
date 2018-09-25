# encoding: utf-8
import build_topology
import tcp_test
import shlex
import subprocess
from subprocess import Popen, PIPE
from multiprocessing import Process
import sys
import os
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.node import RemoteController
from mininet.net import Mininet
from ripl.ripl.dctopo import FatTreeTopo
import time
import networkx

pods = 4;
processList = []

def poxMnFt(adjListFile, routingFile):
	#Start Pox
	print('')
	print("Controlador POX Foi iniciado.")
	command = shlex.split('pox/pox.py DCController --topo=ft,'+ str(pods) +' --routing=ECMP')

	with open(os.devnull, "w") as fnull:
		pPox = Popen(command, stdout=fnull, stderr=fnull)
		processList.append(pPox)

	print("Mininet será iniciado em uma nova janela.")
	#command = shlex.split('sudo lxterm -e mn --custom ripl/ripl/mn.py --topo ft,'+ str(pods) +  ',0.001' +' --controller=remote --mac')
	#TestF
	command = shlex.split('sudo lxterm -e mn --custom ripl/ripl/mn.py --topo ft,'+ str(pods) +' --controller=remote --mac --link tc,bw=10,delay=10ms')
	with open(os.devnull, "w") as fnull:
		pMininet = Popen(command, stdout=fnull, stderr=fnull)
		processList.append(pMininet)


def poxMnJf(numberSwitch, numberPorts, inter_switch_Links, flowsNumber, numHosts, adjListFile, routeringmode,routingFile):	
	#Start Pox
	print('')
	print("Controlador POX Foi iniciado.")
	command = shlex.split('pox/pox.py riplpox.riplpox --topo=jelly,' + str(numberSwitch) + ',' + str(numberPorts) + ',' + adjListFile + ' --routing=jelly,' + routingFile + ' --mode=reactive')
	with open(os.devnull, "w") as fnull:
		pPox = Popen(command, stdout=fnull, stderr=fnull)
		processList.append(pPox)

	
	print("Mininet será iniciado em uma nova janela.")
	#Start Mininet
	command = shlex.split('sudo lxterm -e mn --custom ripl/ripl/mn.py --topo jelly,' + str(numberSwitch) + ','+ str(numberPorts) + ',' + adjListFile + ' --controller=remote --mac --link tc,bw=10,delay=10ms')
	with open(os.devnull, "w") as fnull:
		pMininet = Popen(command, stdout=fnull, stderr=fnull)
		processList.append(pMininet)


def deleteFiles():
	#Delete Results and stop mininet
	os.system('sudo rm -rf results/ecmp_8_/* results/ksp_/* pickled_routes/* transformed_routes/*')
	os.system('clear')

def reproduzFig9():
	numberSwitch = 230
	numberPorts = 10
	inter_switch_Links = 10 #degree
	flowsNumber = 8
	numHosts = 3*numberSwitch	
	# Build Topology
	build_topology.initJfTopo(numberSwitch, inter_switch_Links,numHosts) # Cria topoogia Jellyfish e rotas usando ecmp e ksp
	print("Fig 9 foi reproduzida e encontra-se no diretório 'plots'.")
		

def print_menuJf():
	os.system('clear')
	print('1 - Jellyfish ECMP')
	print('2 - Jellyfish KSP')

def menuFlows():
 	#os.system('clear')
 	#menuF = True
 	while True:
 		choiceFlows= int(raw_input('Digite a quantidade fluxos TCP (1 ou 8) e pressione Enter: '))
 		if choiceFlows == 1 or choiceFlows == 8: 			
 			return choiceFlows


def menuTopology():
	os.system('clear')
	print('Escolha entre as topologias Jellysifh e Fat-tree')
	print('1 - Jellyfish')
	print('2 - Fat-tree')
	choiceTp= int(raw_input('Digite: '))
	if choiceTp == 1:
		return 'jf'
	elif choiceTp == 2:
		return 'ft'
	else:
		return 'sair'

def menuFt(pods, adjListFile):

	os.system('clear')
	print('#### Fat-tree ECMP ####')
	routeringmode = 'ecmp_8_' # ecmp_8_ or ksp_
	flowsNumber = menuFlows()
	#gambiarra pura ;)
	num_hosts = (pods ** 3)/4
	hosts = [(str(i)) for i in range (1, num_hosts + 1)]
	tcp_test.InitTestFt(pods, routeringmode, flowsNumber)


	#print("Foi criado o arquivo 'ecmp_8_scriptFt' para geração de tráfego")
	raw_input("Pressione Enter para continuar")
	routingFile = routeringmode + adjListFile
	#routingFile = 'ecmp_8_graphFt'
	poxMnFt(adjListFile, routingFile)

	print("Nesta nova janela digite 'source ecmp_8_scriptFt' para utilizar o iperf ou 'exit()'' para sair.")
	print("Verique no diretório 'results/ecmp_8_/' o resumo do tráfego apresentado pelo iperf.")
	raw_input("Após verificar a conclusão, pressione Enter para continuar...")
	os.system('clear')
	print('#### Fat-tree ECMP ####')
	menuThroughput('results/ecmp_8_/')

	raw_input("Pressione Enter para continuar...")


def throughputCalculation(directory):
	arquivosDiretorio = os.listdir(directory)
	arquivos = []
	size = len(arquivosDiretorio)
	#verifica se há arquivos nulos:
	for i in range(size):
		if os.stat(directory + '/'+ arquivosDiretorio[i]).st_size != 0:
			arquivos.append(arquivosDiretorio[i])

	size = len(arquivos)
	bandwidthList = []
	
	for i in range(size):

		with open(directory + '/'+ arquivos[i], 'r') as f:
			try:
				lines = f.read().splitlines()
				last_line = lines[-1]
				#print(last_line)
				bandwidth = last_line.split()

				#Cálculo para 8 flows
				if bandwidth[0] == '[SUM]':
					bandwidthList.append(bandwidth[5])
				else: # Cálculos para 1 flow
					#Alguns testes geram apenas kbytes,então:
					if bandwidth[7] == 'Kbits/sec':
						bandwidthList.append(str(float(bandwidth[6])/1024))

					else:
						bandwidthList.append(bandwidth[6])
			except:
				print('Erro na Leitura dos arquivos, conteúdo inesperado')
 				raw_input("Pressione Enter para continuar...")

	

 	try:
 		bandW = [float(i) for i in bandwidthList]
 		Avg = sum(bandW)/len(bandwidthList)
 		print('Largura de banda utilizada:')
 		print(str(Avg)+ ' Mbits/sec')
 		print('')
 		raw_input("Pressione Enter para continuar...")
 	except:
 		print('Erro na Leitura dos dados gerados pelo iperf')
 		raw_input("Pressione Enter para continuar...")


def menuThroughput(directory):
	firsttime = True;
	loopmt = True
	while loopmt:
		if firsttime == False:
			os.system('clear')
			os.system('sudo rm -rf ' + directory + '/*')
			print("Para realizar nova verificação, finalize o iperf utilizando: 'source iperfkill' e utilize novamente o script para geração de tráfego.")
			print("Os arquivos para geração de tráfego foram deletados.")
			print('')
			raw_input("Pressione Enter para continuar...")			
		

		os.system('clear')
		print("Digite '1' para verificar o throughput e '0' para voltar")
		choiceFlows= int(raw_input(''))
		if choiceFlows == 1:
			throughputCalculation(directory)
			firsttime = False;			
			#os.system('clear')
			#print('Volte a janela do mininet e execute novamente o iperf')
			
		elif choiceFlows ==0 :
			loopmt= False
		else:
			print('0 ou 1!!! Eu avisei. Feche o programa ;)')
			raw_input("Pressione Enter para continuar...")
			loopmt = False
		print('')
		print("Para obter novos valores, execute o mesmo script no mininet")
		print('')



def menuJf(numberSwitch, numberPorts, inter_switch_Links, numHosts,adjListFile):
	loopJf = True
	while loopJf:
		print_menuJf()
		choice = int(raw_input('Digite opção [1-2], o outro para sair:'))

		if choice == 1:
			os.system('clear')
			print('#### Jellyfish ECMP ####')
			routeringmode = 'ecmp_8_' # ecmp_8_ or ksp_
			flowsNumber = menuFlows()
			tcp_test.InitTestJf(numberSwitch, numberPorts,adjListFile,flowsNumber,routeringmode)
			#print("Foi criado o arquivo 'ecmp_8_script' para geração de tráfego")
			#raw_input("Pressione Enter para continuar")
			routingFile = routeringmode + adjListFile	
			poxMnJf(numberSwitch, numberPorts, inter_switch_Links, flowsNumber, numHosts, adjListFile, routeringmode,routingFile)
			print("Nesta nova janela digite 'source ecmp_8_scriptJf' para utilizar o iperf ou 'exit()'' para sair.")
			print("Verique no diretório 'results/ecmp_8_/' o resumo do tráfego apresentado pelo iperf.")
			raw_input("Após verificar a conclusão, pressione Enter para continuar...")
			os.system('clear')
			print('#### Jellyfish ECMP ####')
			menuThroughput('results/ecmp_8_/')

			

						
		elif choice == 2:
			os.system('clear')
			print('#### Jellyfish KSP ####')
			routeringmode = 'ksp_' # ecmp_8_ or ksp_
			flowsNumber = menuFlows()
			tcp_test.InitTestJf(numberSwitch, numberPorts,adjListFile,flowsNumber,routeringmode)
			#print("Foi criado o arquivo 'ksp_script' para geração de tráfego")
			routingFile = routeringmode + adjListFile
			poxMnJf(numberSwitch, numberPorts, inter_switch_Links, flowsNumber, numHosts, adjListFile, routeringmode,routingFile)
			print("Nesta nova janela digite 'source ksp_scriptJf' para utilizar o iperf ou 'exit()'' para sair.")
			print("Verique no diretório 'results/ksp_/' o resumo do tráfego apresentado pelo iperf.")
			raw_input("Após verificar a conclusão, pressione Enter para continuar...")
			os.system('clear')
			print('#### Jellyfish KSP ####')
			menuThroughput('results/ksp_/')

					
		else:
			loopJf = False

	#raw_input("Pressione Enter para continuar...")
	os.system('exit')


def start():
	os.system('clear')
	print('Mininet sendo reiniciado, aguarde 1 segundo...')
	print('')

	os.system('sudo mn -c')
	os.system('clear')

	deleteFiles()
	print("Programa iniciado")
	print('Recomenda-se que o programa seja executado umas vez para cada topologia e algoritmo de roteamento.')
	print('Ao finalizar o programa corretamente os processos serão encerrados evitando problemas em execuções futuras.')
	print('')
	raw_input("Pressione Enter para continuar...")


	loopPrincipal = True
	while loopPrincipal:
		optionTp = menuTopology()
		#os.system('clear')
		if optionTp == 'jf':
			while True:
					try:
						numberSwitch = 20
						numberPorts = 4
						inter_switch_Links = 3 #degree
						numHosts = 3*numberSwitch
						adjListFile = "rrg_%s_%s" % (inter_switch_Links, numberSwitch)
						build_topology.initJfTopo(numberSwitch, inter_switch_Links,numHosts) # Cria topoogia Jellyfish e rotas usando ecmp e ksp
						
						print('Criado com Sucesso JF')
						raw_input("Pressione Enter para continuar...")
						menuJf(numberSwitch, numberPorts, inter_switch_Links, numHosts, adjListFile)
						break;
					except:
						print('Erro ao criar JF')
						os.system('clear')
						#raw_input("Pressione Enter para continuar...")


		elif optionTp == 'ft':
			adjListFile = 'graphFt'
			#graphFt = build_topology.initFtTopo(pods)
			#print('Criado com Sucesso Ft')
			#raw_input("Pressione Enter para continuar...")
			menuFt(pods, adjListFile)

		elif optionTp == 'sair':
			loopPrincipal = False

		else:
			print("Este programa não é 'friendly user', ele possui erros ;)")
			loopPrincipal = False
			raw_input("Pressione Enter para continuar...")



if __name__ == "__main__":
	start()
	for i in range(len(processList)):
		processList[i].kill()