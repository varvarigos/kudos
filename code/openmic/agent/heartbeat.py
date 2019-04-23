"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""


import time
import json
import psutil
import logging
import threading

logger = logging.getLogger('openmic.agent.hearbeat')


class HeartBeat:

	def __init__(self, agent_context):

		self.active = False
		self.agent_context = agent_context


	def start(self):
		
		logger.debug("Start heartbeat timer ...")
		self.active = True
		self.callback()
		

	def stop(self):
		
		logger.debug("Stop heartbeat timer ...")
		self.active = False
		

	def callback(self):
		
		if self.active:
			status = self._basic_monitoring()
			heartbeat_msg = {"agent_id": self.agent_context.agent_id, "response_type": "heartbeat", "response_content": status}
			self.agent_context.add_message_to_internal_fwd_queue(heartbeat_msg) 
			threading.Timer(self.agent_context.heartbeat_interval, self.callback, ).start()


	def _basic_monitoring(self):

		status = { }

		memory = psutil.virtual_memory()

		total_memory_mb = int(memory.total)/1024
		free_memory_mb = int(memory.free)/1024
		used_memory_mb = total_memory_mb - free_memory_mb

		memory_utilization = round(float(used_memory_mb)/float(total_memory_mb)*100,2)

		disk = psutil.disk_usage("/")
		
		status["agent_id"] = self.agent_context.agent_id
		status["timestamp"] = int(time.time())
		
		status["total_disk_GB"] = disk[0]
		status["disk_utilization"] = disk[3]

		if int(psutil.__version__.split(".")[0]) > 2 :
			status["cpu_cores"] = int(psutil.cpu_count())
			status["boot_time"] = int(psutil.boot_time())
		else:
			status["cpu_cores"] = int(psutil.NUM_CPUS)   
			status["boot_time"] = int(psutil.get_boot_time())

		status["cpu_utilization"] = psutil.cpu_percent(interval=1)
		status["total_memory_MB"] = total_memory_mb
		status["memory_utilization"] = memory_utilization

		logger.debug("Basic monitoring: %s"%(json.dumps(status)))

		return status