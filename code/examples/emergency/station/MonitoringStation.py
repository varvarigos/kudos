"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""

import sys
import json
import time
import pygame
import os.path
import logging
import threading

import StationSounds
import RPi.GPIO as GPIO

from PyQt5.QtCore import QObject, pyqtSignal

import openmic.lib.events as events
import openmic.lib.constants as constants
import openmic.utils.connection_parameters as cons
import openmic.agent.agent_context as agent_context
import openmic.agent.agent_instance as agent_instance



class MonitoringStation(QObject):

	sound_thread_signal = pyqtSignal(str)

	def __init__(self, station_index) :
		
		super(MonitoringStation, self).__init__()

		self.station_index = station_index

		self.ticks = 0
		self.steps = 5
		self.station_alarm = False
		self.external_alarm = False
		self.led_on = False
		self.agent_instance = None
		self.flash_blinking = False
		self.emit_alarm = False
		self.lookup_table = [[1,1,0,0],[1,1,1,0],[0,1,1,1],[0,0,1,1]]


		self.sound_thread = StationSounds.StationSounds()
		self.sound_thread_signal.connect(self.sound_thread.on_play_sound)
		self.sound_thread.start()
		
		zeromq_params = cons.ZeroMQParameters("127.0.0.1")
		self.context = agent_context.AgentContext(zeromq_params)
		
		#rabbitmq_params = cons.RabbitMQParameters("","", "", virtual_host = "")
		#self.context = agent_context.AgentContext(rabbitmq_params, constants.DRIVER_RABBITMQ)

		## initialize GPIO
		
		GPIO.setmode(GPIO.BOARD)

		GPIO.setup(11, GPIO.OUT)
		GPIO.setup(13, GPIO.OUT)
		GPIO.setup(12, GPIO.IN)
		
		GPIO.output(11, GPIO.LOW)
		GPIO.output(13, GPIO.LOW)
		

	def start(self):

		self.agent_instance = agent_instance.AgentInstance(self.context) 

		self.context.connect([events.EventControllerRequest], self.handle_controller_request)
		self.context.connect([events.EventAgentCollaboration], self.collaboration)


		while True:

			if self.ticks % self.steps == 0 :
				self.led_on = not self.led_on

				if self.led_on :
					GPIO.output(13 if (self.station_alarm or self.external_alarm) else 11, GPIO.HIGH)
				else:
					GPIO.output(13 if (self.station_alarm or self.external_alarm) else 11, GPIO.LOW)

			if GPIO.input(12) == 0 and  self.station_alarm == False: 
				
				self.station_alarm = True
				GPIO.output(11, GPIO.LOW)
				GPIO.output(13, GPIO.HIGH)

				self.lookup_table[self.station_index][self.station_index] = 0

				self.agent_instance.agent_to_agents_request([], { "alarm": self.station_index })
				self.sound_thread_signal.emit(self.get_evacuation_message())


			if self.emit_alarm :
				self.emit_alarm = False
				self.sound_thread_signal.emit(self.get_evacuation_message())

			time.sleep(0.5)
			self.ticks += 1
		
 
	def get_evacuation_message(self):
		
		positions = self.lookup_table[self.station_index]

		if self.station_index == 0 :	

			if positions[0] == 1 :
				return "evacuate_0"
			if positions[1] == 1:
				return "evacuate_1"

		elif self.station_index == 1: 

			if positions[1] == 1 :
				return "evacuate_1"
			if positions[0] == 1:
				return "evacuate_0"
			if positions[2] == 1 :
				return "evacuate_2"

		elif self.station_index == 2:
		
			if positions[2] == 1 :
				return "evacuate_2"
			if positions[1] == 1:
				return "evacuate_1"
			if positions[3] == 1 :
				return "evacuate_3"

		elif self.station_index == 3:

			if positions[3] == 1 :
				return "evacuate_3"
			if positions[2] == 1:
				return "evacuate_2"

		return "no_evacuate"


	def clean_up(self):
		GPIO.output(11, GPIO.LOW)
		GPIO.output(13, GPIO.LOW)
		GPIO.cleanup()


	def collaboration(self, evt):

		self.external_alarm = True
		self.emit_alarm = True

		GPIO.output(11, GPIO.LOW)
		GPIO.output(13, GPIO.HIGH)

		self.lookup_table[self.station_index][int(evt.collaboration_content["alarm"])] = 0

	

	def handle_controller_request(self, evt):

		if evt.request["cmd"] == "led_blinkig" :
			
			self.flash_blinking = not self.flash_blinking

			self.steps = 1 if self.flash_blinking else 5

		if evt.request["cmd"] == "sound_testing" :
			
			pygame.mixer.pre_init(frequency = 16000, channels = 1) 
			pygame.init()
			pygame.mixer.init(frequency = 16000, channels = 1)
			pygame.mixer.music.load("sounds/bell.wav")
			pygame.mixer.music.play()
			while pygame.mixer.music.get_busy() == True:
				continue		
			pygame.quit()


if __name__ == "__main__":

	if len(sys.argv) != 2:
		print("\nUsage: python3 MonitoringStation.py [0|1|2|3]\n")
		sys.exit(0)

	logging.basicConfig(filename = 'monitoring_station.log', level = logging.INFO)

	try:

		station = MonitoringStation(int(sys.argv[1]))

		station.start()

	except KeyboardInterrupt:
		station.clean_up()
		sys.exit(0)
