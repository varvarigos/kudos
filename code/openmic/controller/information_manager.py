"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""

import uuid
import time
import json
import logging
import threading

import openmic.lib.events as events


logger = logging.getLogger('openmic.controller.information_manager')


class InformationManager:

	def __init__(self, app_context):

		self.skip_scanning = True
		self.disconnected_time_limit = 180 #seconds 
		self.disconnected_scan_rate = 120 #seconds

		self.app_context = app_context
		
		self.active_agents_ids = []
		self.agent_latest_heartbeat = {}
		self.agent_assigned_requests = {}

		self.scan_disconnected_agents()


	def scan_disconnected_agents(self):

		purge_agents = []

		if not self.skip_scanning:
			for agent_id in self.agent_latest_heartbeat:
				if (int(time.time()) - self.agent_latest_heartbeat[agent_id]["timestamp"]) > self.disconnected_time_limit :
					purge_agents.append(agent_id)

			for agent_id in purge_agents:
				self.active_agents_ids.remove(agent_id)
				del self.agent_latest_heartbeat[agent_id]
				del self.agent_assigned_requests[agent_id]

			if len(purge_agents) > 0 :
				self.app_context._notify_event_handlers(events.EventAgentsDisconnected(purge_agents))

		self.skip_scanning = False 
		threading.Timer(self.disconnected_scan_rate, self.scan_disconnected_agents).start()


	def handle_agent_heartbeat(self, message):

		agent_discovered = False

		agent_id = message["agent_id"]

		if agent_id not in self.active_agents_ids:		
			agent_discovered = True
			self.active_agents_ids.append(agent_id)
			self.agent_latest_heartbeat[agent_id] = {}
			self.agent_assigned_requests[agent_id] = []

		self.agent_latest_heartbeat[agent_id] = message["response_content"]

		return agent_discovered


	def get_active_agents(self):
		return self.active_agents_ids


	def get_active_agents_information(self, agents_ids):

		agents_information = []

		if agents_ids == None:
			agents_information = list(self.agent_latest_heartbeat.values())
		elif isinstance(agents_ids, list):
			for agent_id in agents_ids:
				if agent_id in self.agent_latest_heartbeat.keys():
					agents_information.append(self.agent_latest_heartbeat[agent_id])
		else:
			if agents_ids in self.agent_latest_heartbeat.keys():
				agents_information = self.agent_latest_heartbeat[agents_ids]

		return agents_information


	def assign_requests_to_agents(self, requests, agents_ids):

		requests_ids = []

		# means broadcast requests to all available agents
		if agents_ids == None:  
			agents_ids = self.active_agents_ids

		for request in requests:

			if not isinstance(request, dict):
				request = json.loads(request)

			for agent_id in agents_ids:
				if agent_id in self.active_agents_ids:
					request_id = str(uuid.uuid4())
					self.agent_assigned_requests[agent_id].append(request_id)
					requests_ids.append(request_id)
					self.app_context.add_message_to_internal_fwd_queue({"agent_id": agent_id, "request_id": request_id, 
																		"request_content": request})
				
		return requests_ids


	def update_request_assignment(self, response):

		if response["agent_id"] not in self.active_agents_ids:
			return False

		self.agent_assigned_requests[response["agent_id"]].remove(response["request_id"])

	
	def pending_requests(self, agent_id):

		if agent_id == None :
			return self.agent_assigned_requests
		else:
			pending = []
			
			if agent_id in self.agent_assigned_requests.keys():
				pending = self.agent_assigned_requests[agent_id]

			return pending