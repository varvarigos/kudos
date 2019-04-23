"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""


import json
import logging

import openmic.lib.exceptions as exceptions
import openmic.agent.heartbeat as heartbeat
import openmic.agent.internal_manager as internalManager
import openmic.agent.communication_interface as communicationInterface


logger = logging.getLogger('openmic.agent.agent_instance')


class AgentInstance:

	def __init__(self, agent_context):

		if agent_context.connection_parameters == None:
			raise exceptions.InvalidContext() 

		self.agent_context = agent_context
		self.communication_interface = communicationInterface.CommunicationInterface(agent_context)
		self.internal_manager = internalManager.InternalManager(agent_context)
		
		self.heartbeat = heartbeat.HeartBeat(agent_context)
		self.heartbeat.start()


	def send_response(self, request_id, response):
		
		normal_response = { "agent_id": self.agent_context.agent_id, "request_id": request_id, "response_type": "normal" }

		if isinstance(response, dict):
			normal_response["response_content"] = response
		else:
			normal_response["response_content"] = json.loads(response)

		self.agent_context.add_message_to_internal_fwd_queue(normal_response)


	def basic_monitoring(self):
		return self.heartbeat._basic_monitoring()


	def available_agents(self):

		query_agents = { "agent_id": self.agent_context.agent_id, "request_id": 0, "response_type": "agents" }
		query_agents["response_content"] = {}

		self.agent_context.add_message_to_internal_fwd_queue(query_agents)


	def agent_to_agents_request(self, agents_ids, request):
	
		a2a_request = { "agent_id": self.agent_context.agent_id, "response_type": "collaboration" }

		if not isinstance(agents_ids, list):
			agents_ids = [agents_ids]

		a2a_request["target_agents_ids"] = agents_ids

		if isinstance(request, dict):
			a2a_request["response_content"] = request
		else:
			a2a_request["response_content"] = json.loads(request)

		self.agent_context.add_message_to_internal_fwd_queue(a2a_request)


	def agent_general_message(self, message):
		
		message = { "agent_id": self.agent_context.agent_id, "response_type": "message" }

		if isinstance(message, dict):
			message_response["response_content"] = message
		else:
			message_response["response_content"] = json.loads(message)

		self.agent_context.add_message_to_internal_fwd_queue(message_response)