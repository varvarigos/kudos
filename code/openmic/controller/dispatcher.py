"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""

import json
import logging

import openmic.lib.events as events
import openmic.controller.information_manager as informationManager
import openmic.controller.communication_interface as communicationInterface

logger = logging.getLogger('openmic.controller.dispatcher')


class Dispatcher:

	def __init__(self, controller_context):

		self.controller_context = controller_context

		self.information_manager = informationManager.InformationManager(controller_context)
		self.communication_interface = communicationInterface.CommunicationInterface(controller_context)

		controller_context._register_internal_event_subscriber(events.CommunicationInterfaceResponse, self.agent_responses)


	def agent_responses(self, response_evt):

		logger.debug("Handle agent response: %s"%(response_evt.response))

		response = json.loads(response_evt.response)

		if response["response_type"] == "heartbeat" :

			is_new_agent = self.information_manager.handle_agent_heartbeat(response)
			if is_new_agent:
				self.controller_context._notify_event_handlers( events.EventAgentConnected( response["agent_id"],
																							response["response_content"]))
			else:
				self.controller_context._notify_event_handlers( events.EventAgentHeartBeat( response["agent_id"],
																							response["response_content"]))

		elif response["response_type"] == "normal" :
			self.information_manager.update_request_assignment(response)
			self.controller_context._notify_event_handlers( events.EventAgentResponse(	response["agent_id"],
																						response["request_id"],
																						response["response_content"]))
		
		elif response["response_type"] == "agents" :
		
			agents_ids = self.information_manager.get_active_agents()

			other_agents = [agent for agent in agents_ids if agent != response["agent_id"]]

			self.controller_context.add_message_to_internal_fwd_queue({	"agent_id": response["agent_id"],
																		"request_id": 0, 
																		"request_content": { "agents": other_agents}})

		elif response["response_type"] == "collaboration" :
		
			all_other_agents = [agent for agent in self.information_manager.get_active_agents() if agent != response["agent_id"]]

			if len(response["target_agents_ids"]) == 0:
				agents = all_other_agents
			else:
				agents = list(set(response["target_agents_ids"]).intersection(set(all_other_agents)))

			for agent_id in agents:			
				self.controller_context.add_message_to_internal_fwd_queue({	"agent_id": agent_id, 
																			"sender_agent_id": response["agent_id"], 
																			"collaboration_content": response["response_content"]})
		elif response["response_type"] == "message" :
			self.controller_context._notify_event_handlers( events.EventAgentGeneralMessage(response["agent_id"],
																							response["response_content"]))


	def get_agents_information(self, agents_ids):
		return self.information_manager.get_active_agents_information(agents_ids)


	def get_agents(self):
		return self.information_manager.get_active_agents()
	

	def handle_requests(self, requests, agents_ids):
		return self.information_manager.assign_requests_to_agents(requests, agents_ids)


	def get_pending_requests(self, agent_id):
		return self.information_manager.pending_requests(agent_id)
