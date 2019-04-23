"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""

import logging

import openmic.lib.exceptions as exceptions
import openmic.controller.dispatcher as dispatcher

logger = logging.getLogger('openmic.controller.controller_instance')

class ControllerInstance():

	def __init__(self, context):

		if context.connection_parameters == None:
			raise exceptions.InvalidContext() 

		self.dispatcher = dispatcher.Dispatcher(context) 


	def terminate(self):
		self.dispatcher.terminate()

	def agents_information(self, agents_ids = None):
		return self.dispatcher.get_agents_information(agents_ids)


	def list_agents(self):
		return self.dispatcher.get_agents()
	

	def forward_request(self, request):

		if not isinstance(request, list):
			request = [request]

		return self.dispatcher.handle_requests(request, None)


	def forward_requests(self, requests):

		if not isinstance(requests, list):
			requests = [requests]

		return self.dispatcher.handle_requests(requests, None)


	def submit_request_to_agent(self, request, agent_id):
		
		if not isinstance(request, list):
			request = [request]

		if not isinstance(agent_id, list):
			agent_id = [agent_id]

		return self.dispatcher.handle_requests(request, agent_id)


	def submit_requests_to_agent(self, requests, agent_id):

		if not isinstance(requests, list):
			requests = [requests]

		if not isinstance(agent_id, list):
			agent_id = [agent_id]

		return self.dispatcher.handle_requests(requests, agent_id)


	def submit_request_to_agents(self, request, agents_ids):

		if not isinstance(request, list):
			request = [request]

		if not isinstance(agents_ids, list):
			agents_ids = [agents_ids]

		return self.dispatcher.handle_requests(request, agents_ids)


	def submit_requests_to_agents(self, requests, agents_ids):

		if not isinstance(requests, list):
			requests = [requests]

		if not isinstance(agents_ids, list):
			agents_ids = [agents_ids]

		return self.dispatcher.handle_requests(requests, agents_ids)


	def pending_requests(self):
		return self.dispatcher.get_pending_requests(None)


	def agent_pending_requests(self, agent_id):

		pending = []

		if agent_id in self.dispatcher.get_agents():
			pending = self.dispatcher.get_pending_requests(agent_id)

		return pending