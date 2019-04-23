
"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""


class ZeroMQParameters:


	def __init__(self, controller_address, agent_to_controller_port = 5579, controller_to_agent_port = 5570):
		self.controller_address = controller_address
		self.push_pull_port = agent_to_controller_port
		self.router_port = controller_to_agent_port
		
	def __getitem__(self, key):
		return getattr(self, key)


class RabbitMQParameters:

	def __init__(self, rabbitmq_server_ip, rabbitmq_username = "guest", rabbitmq_password = "guest", responses_queue = "agent_responses", virtual_host = "/"):
		self.server_ip = rabbitmq_server_ip
		self.username = rabbitmq_username
		self.password = rabbitmq_password
		self.responses_queue = responses_queue
		self.virtual_host = virtual_host

	def __getitem__(self, key):
		return getattr(self, key)
