"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""


import logging
import threading

import openmic.drivers.zeromq as ZMQ
import openmic.drivers.rabbitmq as RMQ
 
import openmic.lib.constants as constants
import openmic.lib.exceptions as exceptions


logger = logging.getLogger('openmic.agent.communication_interface')


class CommunicationInterface:

	def __init__(self, controller_context):

		self.request_worker = None
		self.response_worker = None
		self.driver_request = None
		self.driver_response = None
		
		self.controller_context = controller_context
		self.driver_name = controller_context.driver_name

		self._initialize_driver()


	def _initialize_driver(self):

		if self.driver_name == constants.DRIVER_ZEROMQ :
			self.driver_request = ZMQ.agent_get_requests
			self.driver_response = ZMQ.agent_forward_responses
		elif self.driver_name == constants.DRIVER_RABBITMQ :
			self.driver_request = RMQ.agent_get_requests 
			self.driver_response = RMQ.agent_forward_responses 
		else:
			raise exceptions.UnknownCommunicationDriver(self.driver_name)
	
		self.request_worker = threading.Thread( name = 'Request Worker', target = self.driver_request, 
												args = (self.controller_context,))
		
		self.response_worker = threading.Thread(name = 'Response Worker', target = self.driver_response, 
												args = (self.controller_context,))

		self.request_worker.start()
		self.response_worker.start()