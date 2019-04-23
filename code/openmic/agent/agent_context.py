"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""



import uuid
import os.path
import getpass
import logging

import openmic.lib.constants as constants
import openmic.lib.sync_queue as syncQueue
import openmic.lib.exceptions as exceptions
import openmic.utils.connection_parameters as cons

logger = logging.getLogger('openmic.agent.agent_context')


class AgentContext(object):

	def __init__(self, connection_parameters, driver_name = constants.DRIVER_ZEROMQ):
		
		self._validate_connection_parameters(connection_parameters, driver_name)

		self.connection_parameters = connection_parameters
		self.driver_name = driver_name
		self.internal_fwd_queue = syncQueue.SyncQueue()
		self.internal_event_subscribers = dict()
		self.heartbeat_interval = 60
		self.agent_id = self._load_agent_id()
		self.events_handlers = dict()


	def set_heartbeat_rate(self, heartbeat_rate):
		self.heartbeat_rate = int(heartbeat_rate)


	def update_connection_parameters(self, connection_parameters):
		self.connection_parameters = connection_parameters


	def change_active_driver(self, driver_name):
		self.driver_name = driver_name


	def add_message_to_internal_fwd_queue(self, message):
		self.internal_fwd_queue.add(message) 


	def _validate_connection_parameters(self, connection_parameters, driver_name):

		if driver_name == constants.DRIVER_ZEROMQ and not isinstance(connection_parameters, cons.ZeroMQParameters) :
			raise exceptions.InvalidCommunicationParameters(type(connection_parameters).__name__, driver_name)
		if driver_name == constants.DRIVER_RABBITMQ and not isinstance(connection_parameters, cons.RabbitMQParameters) :
			raise exceptions.InvalidCommunicationParameters(type(connection_parameters).__name__, driver_name)
	
	
	def _load_agent_id(self):

		agent_id = None
		f_location = "/home/%s/.openmic_agent"%(getpass.getuser())

		if os.path.exists(f_location) :
			with open(f_location) as f:
				agent_id = f.readline().strip('\n')
		else:
			agent_id = str(uuid.uuid4())
			with open(f_location, "w") as f:
				f.write(agent_id)
			
		return agent_id


	def _register_internal_event_subscriber(self, event, callback):
		
		if event.__name__ not in self.internal_event_subscribers.keys():
			self.internal_event_subscribers[event.__name__] = [callback]
		else:
			self.internal_event_subscribers[event.__name__].append(callback)


	def _send_internal_event(self, event):

		if event.__class__.__name__ not in self.internal_event_subscribers.keys():
			return None

		for subscriber in self.internal_event_subscribers[event.__class__.__name__]:
			subscriber(event)


	def _notify_event_handlers(self, event):

		event_name = event.__class__.__name__

		if event_name not in self.events_handlers.keys():
			return

		for handler in self.events_handlers[event_name]:
			handler(event)


	def connect(self, events, handler):

		for evt in events:
			if evt.__name__ not in self.events_handlers.keys():
				self.events_handlers[evt.__name__] = [handler]
			else:
				self.events_handlers[evt.__name__].append(hander)