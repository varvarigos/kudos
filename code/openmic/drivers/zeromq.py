"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""


import zmq
import json
import logging

import openmic.lib.events as evts

logger = logging.getLogger('openmic.drivers.zeromq')

"""
.. module:: openmic.drivers.zeromq
  :synopsis: Implementation for OpenMIC Communication Interface based on ZeroMQ messaging library

.. moduleauthor::  

"""

def controller_get_responses(app_context):

	"""Receives agent responses and forwards them to appropriate controller internal component.

		:param app_context: OpenMIC controller context object.
		:type app_context: ControllerContext.
		:returns: None
	"""

	zmq_context = zmq.Context()
	
	zmq_socket = zmq_context.socket(zmq.PULL)
	zmq_socket.bind("tcp://*:%s"%(app_context.connection_parameters["push_pull_port"]))
	

	logger.debug("Controller get responses queue is ready, wait for server messages ....")

	while True:

		response = zmq_socket.recv()
		logger.debug("Receive agent response: %s"%(response))
		app_context._send_internal_event(evts.CommunicationInterfaceResponse(response.decode()))



def controller_forward_requests(app_context):

	
	"""Receives messages from controller components and forwards them to appropriate agent(s).

		:param app_context: OpenMIC controller context object.
		:type app_context: ControllerContext.
		:returns: None
	"""

	zmq_context = zmq.Context()

	zmq_socket = zmq_context.socket(zmq.ROUTER)
	zmq_socket.bind("tcp://*:%s"%(app_context.connection_parameters["router_port"]))
	 

	logger.debug("Controller forward requests queue is ready, wait for server messages ....")

	while True:
		request = app_context.internal_fwd_queue.get()
		logger.debug("Forward server request: %s"%(request))
		zmq_socket.send_multipart([request["agent_id"].encode('utf-8'), json.dumps(request).encode('utf-8')])



def agent_get_requests(app_context):

	"""Receives controller requests and forwards them to appropriate agent internal component.

		:param app_context: OpenMIC agent context object.
		:type app_context: AgentContext.
		:returns: None
	"""

	zmq_context = zmq.Context()

	zmq_socket = zmq_context.socket(zmq.DEALER)
	zmq_socket.setsockopt(zmq.IDENTITY, app_context.agent_id.encode("ascii"))
	zmq_socket.connect("tcp://%s:%s"%(	app_context.connection_parameters["controller_address"],
										app_context.connection_parameters["router_port"]))

	logger.debug("Agent get requests queue is ready, wait for controller messages ....")

	while True:
		request = zmq_socket.recv()
		logger.debug("Receive server request: %s"%(request))
		app_context._send_internal_event(evts.CommunicationInterfaceRequest(request))



def agent_forward_responses(app_context):

	"""Receives response messages from agent and  and forwards them to controller.
	
		:param app_context: OpenMIC agent context object.
		:type app_context: AgentContext.
		:returns: None
	"""

	zmq_context = zmq.Context()

	zmq_socket = zmq_context.socket(zmq.PUSH)
	zmq_socket.connect("tcp://%s:%s"%( 	app_context.connection_parameters["controller_address"], 
										app_context.connection_parameters["push_pull_port"]))

	logger.debug("Agent forward responses is ready, wait for agent messages ....")

	while True:
		
		response = json.dumps(app_context.internal_fwd_queue.get())
		logger.debug("Forward agent response: %s"%(response))
		zmq_socket.send_string(u'%s'%response)