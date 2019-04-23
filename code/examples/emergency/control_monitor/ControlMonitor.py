"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""


import sys
import json
import pygame
import logging

import MainWindow

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import openmic.lib.events as events
import openmic.lib.constants as constants
import openmic.lib.exceptions as exceptions
import openmic.utils.connection_parameters as cons
import openmic.controller.controller_context as controller_context
import openmic.controller.controller_instance as controller_instance

COLORS = [Qt.white, Qt.black, Qt.lightGray, Qt.green, Qt.yellow]

class ControlMonitor(QMainWindow, MainWindow.Ui_MainWindow):

	def __init__(self):
	
		super(ControlMonitor, self).__init__()

		self.stations = { }
		self.instance = None

		self.setupUi(self)

		with open("map.json") as f:
			self.map_data = json.load(f)["map"]
			self.rows = len(self.map_data)
			self.columns = len(self.map_data[0])

		self.setup_actions()
		self.setup_openmic_controller()

		self.refresh_map()
		self.show()



	def setup_openmic_controller(self):

		rabbitmq_params = cons.RabbitMQParameters("bee-01.rmq.cloudamqp.com","mtsapzpt", "udyNqp3nCE9LyFYl7-AXt4Hfg747Qctq", virtual_host = "mtsapzpt")
		context = controller_context.ControllerContext(rabbitmq_params, constants.DRIVER_RABBITMQ)

		self.instance = controller_instance.ControllerInstance(context)
		
		context.connect([events.EventAgentConnected], self.agent_connect)
		context.connect([events.EventAgentsDisconnected], self.agent_disconnect)
		context.connect([events.EventAgentHeartBeat], self.agent_heartbeat)
 

	def setup_actions(self):

		self.actionAbout.triggered.connect(self.credentials)

		self.ledsButton.clicked.connect(self.toggle_led_blinking_rate)
		self.testSoundButton.clicked.connect(self.sound_testing)
		

	def sound_testing(self):

		self.instance.forward_request({"cmd": "sound_testing"})


	def toggle_led_blinking_rate(self):

		self.instance.forward_request({"cmd": "led_blinkig"})


	def refresh_map(self):

		for row in range(self.rows):
			for column in range(self.columns):				
	
				lbl = QLabel()
				lbl.setAutoFillBackground(True) 
				palette = lbl.palette()
				
				if self.map_data[row][column] == 2 :
					lbl.setPixmap(QPixmap(":/images/motion-sensor.png"))

				palette.setColor(lbl.backgroundRole(), COLORS[int(self.map_data[row][column])])

				lbl.setPalette(palette)

				self.gridLayout.addWidget(lbl, row, column)
			

	def credentials(self):

		message = '<b>Ανδρέας Βαρβαρίγος & Αναστάσης Βαρβαρίγος 2019</b><br><br>'
		message += '<a href="https://github.com/varvarigos/kudos">https://github.com/varvarigos/kudos</a><br>'
		message += '<div>Icons made by <a href="https://www.flaticon.com/authors/kiranshastry" title="Kiranshastry">Kiranshastry</a> from <a href="https://www.flaticon.com/" 			    title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" 	title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>'
		message += '<div>Icons made by <a href="https://www.freepik.com/" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" 			    title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>'
		message += '<div>Icons made by <a href="https://www.flaticon.com/authors/smashicons" title="Smashicons">Smashicons</a> from <a href="https://www.flaticon.com/" 			    title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>'
		message += '<div>Icons made by <a href="https://www.flaticon.com/authors/roundicons" title="Roundicons">Roundicons</a> from <a href="https://www.flaticon.com/" 			    title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>'

		dlg = QMessageBox(self)
		dlg.setText(message)
		dlg.setIcon(QMessageBox.Information)
		dlg.show()


	def agent_connect(self, evt):

		if evt.agent_id not in self.stations :
			self.stations[evt.agent_id] = { "status": 1, "alarm":0 }
		else:
			self.stations[evt.agent_id]["status"] = 1

		self.refresh_map()


	def agent_disconnect(self, evt):

		for agent_id in evt.agents_ids:
			self.stations[agent_id]["status"] = 0 

		self.refresh_map()

		self.critical_message("Απώλεια επικοινωνίας με τους ακόλουθους σταθμούς παρατήρησης: %s"%(" , ".join(evt.agents_ids)))


	def agent_heartbeat(self, evt):
		print(str(evt))
 

	def critical_message(self, msg):
		
		dlg = QMessageBox(self)
		dlg.setText(msg)
		dlg.setIcon(QMessageBox.Critical)
		dlg.show()


if __name__ == '__main__':

	logging.basicConfig(filename = 'control_monitor.log', level = logging.INFO)

	app = QApplication([])	
	app.setApplicationName("Emergency - Control Monitor")
	window = ControlMonitor()

	app.exec_()
