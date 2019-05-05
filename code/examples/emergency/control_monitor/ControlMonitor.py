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

"""
  Η βασική κλάση κληρονομεί απο την κλάση QMainWindow της βιβλιοθήκης PyQt5 καθως περιλαμβάνει τόσο την 
  υλοποίηση της λογικής της εφαρμογής όσο και της γραφικής διεπαφής.
  
  Ο σχεδιασμός της γραφικής διεπαφής (ui/MainWindow.ui) έγινε με την βοήθεια του διαθέσιμου εργαλείου Qt Designer 
  ενώ για την δημιουργία του σχετικού κώδικα (MainWindow.py) χρησιμοποιήσαμε την εντολή pyuic5.
  
"""
class ControlMonitor(QMainWindow, MainWindow.Ui_MainWindow):

	# Ορίζουμε 2 βοηθητικά signals χρησιμοποιώντας την βιβλιοθήκη PyQt5, αφορούν αποκλειστικά
	# λειτουργίες που σχετίζονται με την λειτουργία της γραφικής διεπαφής
	refresh_signal = pyqtSignal()
	agent_disconnects_signal = pyqtSignal(events.EventAgentsDisconnected)

	def __init__(self):
	
		super(ControlMonitor, self).__init__()
		
		self.instance = None
		self.stations_status = []
		self.stations_agent_id = {}

		self.setupUi(self)

		# Διαβάζουμε το αρχείο map.json που περιέχει την απεικόνιση του χώρου
		# που εμφανίζεται στην γραφική διεπαφή του κέντρου ελέγχου
		with open("map.json") as f:
			data = json.load(f)
			self.map_data = data["map"]
			self.rows = len(self.map_data)
			self.columns = len(self.map_data[0])

			for i in range(data["stations"]):
				self.stations_status.append(0) 
 
		self.setup_actions()
		self.setup_openmic_controller()

		self.refresh_map()
		self.show()


	def setup_openmic_controller(self):
		
		# Καθορίζουμε την παράμετρο για την διεπαφή επικοινωνίας με βάση το ZeroMQ 
		zeromq_params = cons.ZeroMQParameters("127.0.0.1")
		
		# Δημιουργία αντικειμένου της βοηθητικής κλάσης ControllerContext με βάση τις παραμέτρους για την διεπαφή επικοινωνίας
		context = controller_context.ControllerContext(zeromq_params)

		"""
		   Αν θέλουμε να χρησιμοποιήσουμε την διεπαφή επικοινωνίας με βάση το RabbitMQ θα πρέπει να σχολιαστούν οι
		   δυο παραπάνω γραμμές και να βγούν απο τα σχόλια οι επόμενες δύο, αφού πρώτα ορίσουμε τις κατάλληλες
		   παραμέτρους στην RabbitMQParameters 
		"""
		#rabbitmq_params = cons.RabbitMQParameters("","", "", virtual_host = "")
		#context = controller_context.ControllerContext(rabbitmq_params, constants.DRIVER_RABBITMQ)
		
		# Δημιουργούμε το αντικείμενο της βασικής κλάσης ControllerInstance που παρέχει τις λειτουργίες της
		# βιβλιοθήκης OpenMIC στην εφαρμογή μας
		self.instance = controller_instance.ControllerInstance(context)
		
		# Μας ενδιαφέρει να παρακολουθούμε 4 απο τα μηνύματα που σχετίζονται με την επικοινωνία μεταξύ της 
		# εφαρμογής ελέγχου και διαχείρισης και των ειδικών εφαρμογών, έτσι κάνουμε εγγραφή στα αντίστοιχα events 
		# ορίζουμε τις μεθόδους που θέλουμε να τα χειρίζονται
		context.connect([events.EventAgentConnected], self.agent_connect)
		context.connect([events.EventAgentsDisconnected], self.agent_disconnect)
		context.connect([events.EventAgentHeartBeat], self.agent_heartbeat)
		context.connect([events.EventAgentGeneralMessage], self.agent_message)

		# Συσχετίζουμε τα 2 βοηθητικά signals που ορίσαμε στην αρχή της κλάσης με τις μεθόδους που τα χειρίζονται
		self.refresh_signal.connect(self.refresh_map)
		self.agent_disconnects_signal.connect(self.disconnect_alert)

	"""
	   Η παρακάτω μέθοδος χρησιμοποιεί τον μηχανισμό χειρισμού γεγονότων σε στοιχεία της γραφικής
	   διεπαφής της PyQt5 για να ορίσει τις μεθόδους που εκτελούν τις αντίστοιχες ενέργειες.
	   Πρόκειται για ενέργειες που σχετίζονται με την γραφική διεπαφή και την βιβλιοθήκη PyQt5 και οχι
	   με την βιβλιοθήκη OpenMIC.
	"""		
	def setup_actions(self):

		# Menu action
		self.actionAbout.triggered.connect(self.credentials)

		# Actions για τα buttons 
		self.ledsButton.clicked.connect(self.toggle_led_blinking_rate)
		self.testSoundButton.clicked.connect(self.sound_testing)
		
	"""
	   Προωθεί σε όλους τους διαθέσιμους σταθμούς την εντολή που αντιστοιχεί στον έλεγχο ήχου
	"""
	def sound_testing(self):

		self.instance.forward_request({"cmd": "sound_testing"})

	"""
	   Προωθεί σε όλους τους διαθέσιμους σταθμούς την εντολή που αντιστοιχεί στην αλλαγή του
	   ρυθμού που λειτουργούν τα LEDs
	"""
	def toggle_led_blinking_rate(self):

		self.instance.forward_request({"cmd": "led_blinkig"})

		
	"""
	   Ανανεώνει την απεικόνιση του χώρου στη γραφική διεπαφή
	"""
	def refresh_map(self):

		stations = 0

		for row in range(self.rows):
			for column in range(self.columns):				
	
				lbl = QLabel()
				lbl.setAutoFillBackground(True) 
				palette = lbl.palette()
				
				if self.map_data[row][column] == 2 :
			
					lbl.setPixmap(QPixmap(":/images/motion-sensor.png"))
					
					if self.stations_status[stations] == 1 :
						palette.setColor(lbl.backgroundRole(), Qt.lightGray)
					else:
						palette.setColor(lbl.backgroundRole(), Qt.red)

					if self.stations_status[stations] == -1:
						self.critical_message("Συναγερμός - Εντοπίστηκε πρόβλημα απο σταθμό παρατήρησης: Σ%s"%(stations+1))


					stations += 1
			
				else:
					palette.setColor(lbl.backgroundRole(), COLORS[int(self.map_data[row][column])])

				lbl.setPalette(palette)

				self.gridLayout.addWidget(lbl, row, column)
			
	"""
	  Εμφανίζει το παράθυρο με τις πληροφορίες σχετικά με την εφαρμογή
	"""
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


	"""
	  Ενημερώνει το χρήστη όταν εντοπιστεί κάποια απώλεια επικοινωνίας με κάποιο σταθμό
	"""
	def disconnect_alert(self, evt):	
		self.critical_message("Απώλεια επικοινωνίας με τους ακόλουθους σταθμούς παρατήρησης: %s"%(" , ".join(evt.agents_ids)))

	"""
	   Χειρίζεται τα events απο την βιβλιοθήκη OpenMIC σχετικά με την αναγνώριση σύνδεσης απο κάποιο σταθμό
	"""
	def agent_connect(self, evt):

		# Ενημερώνουμε κατάλληλα τις βοηθητικές μεταβλητές
		if evt.agent_id not in self.stations_agent_id :
			self.stations_agent_id[evt.agent_id] = { "station_index": -1 }
		else:
			station_index = self.stations_agent_id[evt.agent_id]["station_index"]
			self.stations_status[station_index] = 1

		# Στέλνουμε ένα σήμα στην γραφική διεπαφή ώστε να ανανεωθεί η απεικόνιση του χώρου 
		self.refresh_signal.emit()

	
	"""
	   Χειρίζεται τα events απο την βιβλιοθήκη OpenMIC σχετικά με την αναγνώριση σύνδεσης απο κάποιο σταθμό
	"""
	def agent_disconnect(self, evt):
		
		# Ενημερώνουμε κατάλληλα τις βοηθητικές μεταβλητές
		for agent_id in evt.agents_ids:
			self.stations_status[self.stations_agent_id[agent_id]["station_index"]] = 0

		# Στέλνουμε ένα σήμα στην γραφική διεπαφή ώστε να ανανεωθεί η απεικόνιση του χώρου 
		self.agent_disconnects_signal.emit(evt)

	"""
	  Χειρίζεται events απο την βιβλιοθήκη OpenMIC σχετικά με την λήψη γενικών μηνυμάτων από κάποιο σταθμό
	"""
	def agent_message(self, evt):
		
		# Ενημερώνουμε κατάλληλα τις βοηθητικές μεταβλητές
		self.stations_agent_id[evt.agent_id]["station_index"] = evt.message["station_index"]
		self.stations_status[evt.message["station_index"]] = evt.message["status"]
		
		# Στέλνουμε ένα σήμα στην γραφική διεπαφή ώστε να ανανεωθεί η απεικόνιση του χώρου 
		self.refresh_signal.emit()


	def agent_heartbeat(self, evt):
		print(str(evt))
 

	def critical_message(self, msg):
		
		dlg = QMessageBox(self)
		dlg.setText(msg)
		dlg.setIcon(QMessageBox.Critical)
		dlg.show()

		
"""
 Το βασικό σημείο απο το οποίο ξεκινά η εκτέλεση του προγράμματος
"""
if __name__ == '__main__':

	logging.basicConfig(filename = 'control_monitor.log', level = logging.INFO)

	app = QApplication([])	
	app.setApplicationName("Emergency - Control Monitor")
	
	# Δημιουργούμε ένα αντικείμενο της κλάσης ControlMonitor που έχουμε υλοποιήσει και περιλαμβάνει
	# την γραφική διεπαφή (βασίζεται στη βιβλιοθήκη PyQt5) και τη λογική της εφαρμογής ελέγχου και διαχείρισης (βασίζεται 
	# στην βιβλιοθήκη OpenMIC
	window = ControlMonitor()

	app.exec_()
