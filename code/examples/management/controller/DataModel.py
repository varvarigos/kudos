
"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""
import json
import time
import uuid

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Raspberry:

	def __init__(self, message):
		
		self.name = message.agent_id
		self.agent_id = message.agent_id
		self.basic_status = message.heartbeat
		self.status_icon = QIcon(":/images/plug.png")
		self.online_status = True
		self.software_inventory = None
		self.hardware_inventory = None
		self.newly_discovered = True 


	def set_name(self, name):
		
		self.name = name


	def update(self, message):
		
		self.basic_status = message.heartbeat
		self.status_icon = QIcon(":/images/plug.png")
		self.online_status = True
		self.newly_discovered = False


	def disconnected(self):
		
		self.status_icon = QIcon(":/images/unplugged.png")
		self.online_status = False



class Task:

	def __init__(self, category, name, parameters):
		
		self.category = category
		self.name = name
		self.parameters = parameters

	def format_agent_request(self):
	
		if self.category <= 2 :
			cmd = "inventory"
		elif self.category == 3 :
			cmd = "shell_command"
		elif self.category == 4 :
			cmd = "simple_command"
		elif self.category == 5 :
			cmd = "install_package"
		elif self.category == 6 :
			cmd = "uninstall_package"

		return json.dumps({"cmd": cmd, "params": self.parameters})


class TaskResults:

	def __init__(self, task):
		self.timestamp = int(time.time())
		self.task_category = task.category
		self.task_name = task.name
		self.agent_request = task.format_agent_request()
		self.results = None


class DataModel:

	def __init__(self, agentsComboBox, tasksComboBox, showTaskAgentsComboBox):

		self.tasks = []
		self.agents = {}
		self.task_results = {}

		self.agentsComboBox = agentsComboBox
		self.tasksComboBox = tasksComboBox
		self.showTaskAgentsComboBox = showTaskAgentsComboBox
		

	def handle_agent_data(self, message):

		if message.agent_id not in self.agents.keys() :
			agent = Raspberry(message)
			self.agents[agent.agent_id] = agent
			self.agentsComboBox.addItem(QIcon(":/images/plug.png"), agent.name, agent.agent_id)
			self.showTaskAgentsComboBox.addItem(QIcon(":/images/plug.png"), agent.name, agent.agent_id)
		else:
			agent = self.agents[message.agent_id]
			agent.update(message)
			self.agents[message.agent_id] = agent
			
			index = list(self.agents.keys()).index(message.agent_id)
			self.agentsComboBox.setItemIcon(index, agent.status_icon)
			self.showTaskAgentsComboBox.setItemIcon(index, agent.status_icon)



	def handle_agent_disconnection(self, message):
		
		for agent_id in message.agents_ids:
			agent = self.agents[agent_id]
			agent.disconnected()
			self.agents[agent_id] = agent

			index = list(self.agents.keys()).index(agent_id)
			self.agentsComboBox.setItemIcon(index, agent.status_icon)
			self.showTaskAgentsComboBox.setItemIcon(index, agent.status_icon)



	def handle_agent_response(self, message):

		if message.request_id in list(self.task_results.keys()):
		
			self.task_results[message.request_id].results = message.response["output"]

			if self.task_results[message.request_id].task_category == 0 :
				self.agents[message.agent_id].hardware_inventory = message.response["output"]["hardware"]
			elif self.task_results[message.request_id].task_category == 1:
				self.agents[message.agent_id].software_inventory = message.response["output"]["software"]			
			elif self.task_results[message.request_id].task_category == 2: 
				self.agents[message.agent_id].hardware_inventory = message.response["output"]["hardware"]
				self.agents[message.agent_id].software_inventory = message.response["output"]["software"]

			return True

		else:

			index = list(self.agents.keys()).index(message.agent_id)
			self.agentsComboBox.setItemText(index, message.response["output"]["hardware"]["machine_name"])
			self.showTaskAgentsComboBox.setItemText(index, message.response["output"]["hardware"]["machine_name"])

			self.agents[message.agent_id].name = message.response["output"]["hardware"]["machine_name"]
			self.agents[message.agent_id].hardware_inventory = 	message.response["output"]["hardware"]
	
			return False


	def create_task(self, category, name, parameters):
		
		task = Task(category, name, parameters)
		self.tasks.append(task)
		self.tasksComboBox.addItem(name)
		self.tasksComboBox.setCurrentIndex(0)


	def delete_task(self, index):
		
		self.tasks.pop(index)
		self.tasksComboBox.clear()

		for task in self.tasks:
			self.tasksComboBox.addItem(task.name)

		if len(self.tasks) > 0 :
			self.tasksComboBox.setCurrentIndex(0)
		

	def submit_task(self, task_index):
		
		return TaskResults(self.tasks[task_index])


	def map_task_to_results(self, task, request_id):

		self.task_results[request_id] = task



	def get_task_results(self, request_id):

		return self.task_results[request_id].results 


	def get_agent(self, agent_id):
		
		return self.agents[agent_id]


	def get_task(self, index):

		return self.tasks[index]


	def get_agent_hardware(self, agent_id):
		
		html = ""

		hardware = self.agents[agent_id].hardware_inventory

		if hardware != None :

			html =  'Name: %s\n'%(hardware["machine_name"])
			html += '\nCPU\nCores: %s  -  Utilization: %s (%%)\n'%(hardware["cpu_cores"], hardware["cpu_utilization"])		
			html += '\nDisk\nTotal Size (GB): %s  -  Utilization: %s (%%)\n'%(hardware["total_disk_GB"], hardware["disk_utilization"])	
			html += '\nMemory\nTotal Size (MB): %s  -  Utilization: %s (%%)\n'%(hardware["total_memory_MB"], hardware["memory_utilization"])		
			html += '\nNetwork Interfaces\n'
			
			for iface in list(hardware["network_interfaces"].keys()):
				html += "\t%s"%(iface)
				for inf in list(hardware["network_interfaces"][iface].keys()):
					html += "\t\t %s - %s"%(inf, str(hardware["network_interfaces"][iface][inf]))
				
		return html
		

	def get_agent_software(self, agent_id):

		software = self.agents[agent_id].software_inventory

		if software != None :
			return "\n".join(software)
		else:
			return ""

