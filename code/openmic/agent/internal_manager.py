"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""

import json
import logging

import openmic.lib.events as events
import openmic.lib.exceptions as exceptions

logger = logging.getLogger('openmic.agent.internal_manager')


class InternalManager:

	def __init__(self, agent_context):

		self.pending_requests = {}
		
		self.agent_context = agent_context

		self.agent_context._register_internal_event_subscriber(events.CommunicationInterfaceRequest, self.request_handler)


	def request_handler(self, evt):

		request = json.loads(evt.request)

		if request["agent_id"] != self.agent_context.agent_id:
			return False

		if "sender_agent_id" in request:

			self.agent_context._notify_event_handlers(events.EventAgentCollaboration(request["agent_id"],
																					request["sender_agent_id"],
																					request["collaboration_content"]))
		else:

			if request["request_id"] != 0 :

				self.pending_requests[request["request_id"]] = request["request_content"]

				self.agent_context._notify_event_handlers(events.EventControllerRequest(request["agent_id"],
																						request["request_id"],
																						request["request_content"]))
			else:
				self.agent_context._notify_event_handlers(events.EventAvailableAgents(request["request_content"]["agents"]))


	def response_handler(self, request_id, response):

		if request_id in self.pending_requests.keys():
			del self.pending_requests[request_id]

		response_msg = { "agent_id": self.agent_context.agent_id, "response_type": "normal", "response_content": response }
		
		self.agent_context.add_message_to_internal_fwd_queue(response_msg) 
