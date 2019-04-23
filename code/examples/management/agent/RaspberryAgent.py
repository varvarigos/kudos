
"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""

import time
import json
import logging

import agent_operations

import openmic.lib.events as events
import openmic.lib.constants as constants
import openmic.utils.connection_parameters as cons
import openmic.agent.agent_context as agent_context
import openmic.agent.agent_instance as agent_instance


class RaspberryAgent:


	def __init__(self) :
		
		self.panding_requests = {}

		zeromq_params = cons.ZeroMQParameters("127.0.0.1")
		self.context = agent_context.AgentContext(zeromq_params)

		#rabbitmq_params = cons.RabbitMQParameters("bee-01.rmq.cloudamqp.com","mtsapzpt", "udyNqp3nCE9LyFYl7-AXt4Hfg747Qctq", virtual_host = "mtsapzpt")
		#self.context = agent_context.AgentContext(rabbitmq_params, constants.DRIVER_RABBITMQ)
		

	def start(self):

		self.agent_instance = agent_instance.AgentInstance(self.context) 

		self.context.connect([events.EventControllerRequest], self.handle_controller_request)


	def handle_controller_request(self, evt):

		request = evt.request

		if request["cmd"] == "inventory" :

			if len(request["params"]) == 0 :
				params = 2
			else:
				params = int(request["params"])

			response = agent_operations.inventory(params)
		
		if request["cmd"] == "shell_command" :
			response = agent_operations.execute_shell_command(request["params"])

		if request["cmd"] == "simple_command" :
			response = agent_operations.execute_simple_command(request["params"])

		if request["cmd"] == "install_package" :
			response = agent_operations.install_package(request["params"])

		if request["cmd"] == "uninstall_package" :
			response = agent_operations.uninstall_package(request["params"])

		self.agent_instance.send_response(evt.request_id, response)
		

if __name__ == "__main__":

	logging.basicConfig(filename = 'agent.log', level = logging.INFO)

	agent = RaspberryAgent()

	agent.start()
