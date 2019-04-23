
"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""


import json
import pika
import logging

import openmic.lib.events as evts

logger = logging.getLogger('openmic.drivers.rabbitmq')


"""
.. module:: openmic.drivers.rabbitmqra
  :synopsis: Implementation for OpenMIC Communication Interface based on RabbitMQ open source message broker

.. moduleauthor:: 

"""

def controller_get_responses(app_context):

	"""Receives agent responses and forwards them to appropriate controller internal component.

		:param app_context: OpenMIC controller context object.
		:type app_context: ControllerContext.
		:returns: None
	"""

	connection_credentials = pika.PlainCredentials( app_context.connection_parameters["username"], 
													app_context.connection_parameters["password"])

	connection_parameters = pika.ConnectionParameters(	host = app_context.connection_parameters["server_ip"],
													  	virtual_host = app_context.connection_parameters["virtual_host"],
													  	credentials = connection_credentials,
													  	blocked_connection_timeout = 5)

	connection = pika.BlockingConnection(connection_parameters)
	channel = connection.channel()
	channel.queue_declare(queue = app_context.connection_parameters["responses_queue"])

	logger.debug("Controller responses queue is ready, waiting for messages ...")

	def callback(ch, method, properties, body):
		logger.debug("Receive agent response/message: %s"%(body))
		app_context._send_internal_event(evts.CommunicationInterfaceResponse(body.decode()))

	channel.basic_consume(queue = app_context.connection_parameters["responses_queue"], on_message_callback = callback, auto_ack = True)
	channel.start_consuming()


def controller_forward_requests(app_context):

	"""Receives messages from controller components and forwards them to appropriate agent(s).

		:param app_context: OpenMIC controller context object.
		:type app_context: ControllerContext.
		:returns: None
	"""

	connection_credentials = pika.PlainCredentials( app_context.connection_parameters["username"], 
													app_context.connection_parameters["password"])

	connection_parameters = pika.ConnectionParameters(	host = app_context.connection_parameters["server_ip"],
														virtual_host = app_context.connection_parameters["virtual_host"],
													  	credentials = connection_credentials,
													  	blocked_connection_timeout = 5)
	
	connection = pika.BlockingConnection(connection_parameters)
	channel = connection.channel()
	channel.exchange_declare(exchange='openmic_agents',exchange_type='topic')

	logger.debug("Controller forward requests queue is ready, wait for server messages ....")

	while True:
		request = app_context.internal_fwd_queue.get()
		logger.debug("Forward server request: %s"%(request))	
		channel.basic_publish(exchange = 'openmic_agents', routing_key = request["agent_id"], body = json.dumps(request))
	


def agent_get_requests(app_context):

	"""Receives controller requests and forwards them to appropriate agent internal component.

		:param app_context: OpenMIC agent context object.
		:type app_context: AgentContext.
		:returns: None
	"""

	connection_credentials = pika.PlainCredentials( app_context.connection_parameters["username"], 
													app_context.connection_parameters["password"])

	connection_parameters = pika.ConnectionParameters(	host = app_context.connection_parameters["server_ip"],
														virtual_host = app_context.connection_parameters["virtual_host"],
													  	credentials = connection_credentials,
													  	blocked_connection_timeout = 5)
	
	connection = pika.BlockingConnection(connection_parameters)
	channel = connection.channel()
	channel.exchange_declare(exchange='openmic_agents', exchange_type='topic')

	result = channel.queue_declare(queue = '', exclusive=True)
	queue_name = result.method.queue
	channel.queue_bind(exchange = 'openmic_agents', queue = queue_name, routing_key = app_context.agent_id)

	logger.debug("Agent get requests queue is ready, wait for controller messages ....")

	def callback(ch, method, properties, body):
		logger.debug("Receive controller request: %s"%(body.decode()))
		app_context._send_internal_event(evts.CommunicationInterfaceRequest(body.decode()))

	channel.basic_consume(queue = queue_name, on_message_callback = callback, auto_ack = True)


	channel.start_consuming()


def agent_forward_responses(app_context):
	
	"""Receives response messages from agent and  and forwards them to controller.
	
		:param app_context: OpenMIC agent context object.
		:type app_context: AgentContext.
		:returns: None
	"""

	connection_credentials = pika.PlainCredentials( app_context.connection_parameters["username"], 
													app_context.connection_parameters["password"])

	connection_parameters = pika.ConnectionParameters( 	host = app_context.connection_parameters["server_ip"],
														virtual_host = app_context.connection_parameters["virtual_host"],
													   	credentials = connection_credentials,
													   	blocked_connection_timeout = 5)

	connection = pika.BlockingConnection(connection_parameters)
	channel = connection.channel()
	channel.queue_declare(queue = app_context.connection_parameters["responses_queue"])

	logger.debug("Agent forward responses is ready, wait for agent messages ....")

	while True:
		response = json.dumps(app_context.internal_fwd_queue.get())
		logger.debug("Forward agent response: %s"%(response))
		channel.basic_publish(  exchange = '', 
								routing_key = app_context.connection_parameters["responses_queue"], 
								body = response )