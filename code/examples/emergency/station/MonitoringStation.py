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

	# Ορίζουμε 1 βοηθητικο signals χρησιμοποιώντας την βιβλιοθήκη PyQt5, αφορα την διαχείριση του
	# thread μέσω του οποίου γίνεται η αναπαραγωγή των ηχητικών μηνυμάτων
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

		# Αρχικοποιούμε το thread που είναι υπεύθυνο για την αναπαραγωγή των αρχείων ήχου
		self.sound_thread = StationSounds.StationSounds()
		
		# Συσχετίζουμε το signal που ορίσαμε πιο πάνω με την μέθδο on_play_sound του thread
		self.sound_thread_signal.connect(self.sound_thread.on_play_sound)
		
		# Ξεκινάμε την εκτέλεση του thread
		self.sound_thread.start()

		# Καθορίζουμε την παράμετρο για την διεπαφή επικοινωνίας με βάση το ZeroMQ
		# Σημείωση: Αν η εφαρμογή ελέγχου και διαχείρισης δεν είναι στο ίδιο μηχάνημα με την ειδική
		#           εφαρμογή θα πρέπει να αντικατασταθεί κατάλληλα η δικτυακή διεύθυνση 
		zeromq_params = cons.ZeroMQParameters("127.0.0.1")
		
		# Δημιουργία αντικειμένου της βοηθητικής κλάσης AgentContext με βάση τις παραμέτρους για την διεπαφή επικοινωνίας
		self.context = agent_context.AgentContext(zeromq_params)
		
		"""
		   Αν θέλουμε να χρησιμοποιήσουμε την διεπαφή επικοινωνίας με βάση το RabbitMQ θα πρέπει να σχολιαστούν οι
		   δυο παραπάνω γραμμές και να βγούν απο τα σχόλια οι επόμενες δύο, αφού πρώτα ορίσουμε τις κατάλληλες
		   παραμέτρους στην RabbitMQParameters 
		"""
		#rabbitmq_params = cons.RabbitMQParameters("","", "", virtual_host = "/")
		#self.context = agent_context.AgentContext(rabbitmq_params, constants.DRIVER_RABBITMQ)

		# Αρχικοποιούμε την βιβλιοθήκη για τον χειρισμό των GPIO pins και καθορίζουμε
		# όλες τις απαραίτητες παραμέτρους
		GPIO.setmode(GPIO.BOARD)

		GPIO.setup(11, GPIO.OUT) # Μπλε LED
		GPIO.setup(13, GPIO.OUT) # Κόκκινο LED
		GPIO.setup(12, GPIO.IN)  # Αισθητήρας
		
		GPIO.output(11, GPIO.LOW)
		GPIO.output(13, GPIO.LOW)
		

	def start(self):

		# Δημιουργούμε το αντικείμενο της βασικής κλάσης AgentInstance που παρέχει τις λειτουργίες της
		# βιβλιοθήκης OpenMIC στην εφαρμογή μας
		self.agent_instance = agent_instance.AgentInstance(self.context) 

		# Μας ενδιαφέρει να παρακολουθούμε για εντολές απο την εφαρμογή ελέγχου και για μηνύματα συνεργασίας
		# απο άλλους σταθμούς, έτσι κάνουμε εγγραφή για τα αντίστοιχα events και οριζουμε την μέθοδο που
		# θα χειρίζεται το κάθε ένα
		self.context.connect([events.EventControllerRequest], self.handle_controller_request)
		self.context.connect([events.EventAgentCollaboration], self.collaboration)

		# Στέλνουμε ένα γενικό μήνυμα στην εφαρμογή ελέγχου ώστε να γνωρίζει ότι ο συγκεκριμένος 
		# σταθμός έχει αρχίσει την λειτουργία του
		self.agent_instance.agent_general_message({"station_index": self.station_index, "status": 1})

		# Στην συνέχεια ελέγχουμε διαρκώς τον αισθητήρα για πιθανό γεγονός και προσαρμόζουμε αν 
		# χρειαστεί το ρυθμό στα LEDs
		while True:

			if self.ticks % self.steps == 0 :
				self.led_on = not self.led_on

				if self.led_on :
					GPIO.output(13 if (self.station_alarm or self.external_alarm) else 11, GPIO.HIGH)
				else:
					GPIO.output(13 if (self.station_alarm or self.external_alarm) else 11, GPIO.LOW)

			# Αν ο αισθητήρα έχει εντοπίσει πρόβλημα και είναι η πρώτη φορά τότε εκτελούμε
			# τις απαραίτητες ενέργειες (μετά δεν χρειάζεται καθώς το μήνυμα παίζει διαρκώς και 
			# ενημερώνεται από άλλες μεθόδους αν χρειαστεί)
			if GPIO.input(12) == 0 and  self.station_alarm == False: 
				
				# ανανεώνουμε την βοηθητική μεταβλητή και κάνουμε πλεον ενεργό το κόκκινο LED
				self.station_alarm = True
				GPIO.output(11, GPIO.LOW)
				GPIO.output(13, GPIO.HIGH)

				# Ανανεώνουμε κατάλληλα τις πληροφορίες στον πίνακα κατάστασης
				self.lookup_table[self.station_index][self.station_index] = 0

				# Στέλνουμε το κατάλληλο μήνυμα προς όλους τους άλλους σταθμούς να ενημερωθούν οτι ο
				# συγκεκριμένος σταθμός έχει εντοπίσει πρόβλημα ώστε να ενεργήσουν κατάλληλα
				self.agent_instance.agent_to_agents_request([], { "alarm": self.station_index })
				
				# Ενημέρωνουμε το κέντρο ελέγχου 
				self.agent_instance.agent_general_message({"station_index": self.station_index, "status": -1})
				
				# Ενημερώνουμε το thread που χειρίζεται τα ηχητικά μηνύματα για το μήνυμα που πρέπει να αναπαραχθεί
				self.sound_thread_signal.emit(self.get_evacuation_message())

			# Αντιστοιχεί στην περίπτωση που ο συγεκριμένος σταθμός δεν έχει εντοπίσει πρόβλημα αλλά έχει
			# ειδοποιηθεί απο κάποιον άλλον
			if self.emit_alarm : 
				self.emit_alarm = False
				self.sound_thread_signal.emit(self.get_evacuation_message())

			# περιμένουμε μισο δευτερόλεπτο πριν παμε στην επόμενη εκτέλεση
			time.sleep(0.5)
			self.ticks += 1
	
	"""
	  Χρησιμοποιεί τις πληροφορίες που περιέχει ο πινακας κατάστασης για να προσδιορίσει το 
	  κατάλληλο ηχητικό μήνυμα
	"""
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


	"""
	  Χειρίζεται τον ομαλό τερματισμό της GPIO βιβλιοθήκης κατά τον τερματισμό της εφαρμογής
	"""
	def clean_up(self):
		GPIO.output(11, GPIO.LOW)
		GPIO.output(13, GPIO.LOW)
		GPIO.cleanup()


	"""
	  Χειρίζεται τα μηνύματα συνεργασίας από κάποιο άλλο σταθμό 
	"""		
	def collaboration(self, evt):

		# Ανανενώνουμε τις βοηθητικές μεταβλητες
		self.external_alarm = True
		self.emit_alarm = True

		# Αλλαζουμε το ενεργό LED απο μπλέ σε κόκκινο 
		GPIO.output(11, GPIO.LOW)
		GPIO.output(13, GPIO.HIGH)

		# Ανανεώνουμε τις πληροφορίες στον πίνακα κατάστασης  με βαση τον οποίο η εφαρμογή 
		# αποφασίζει για το κατάλληλο ηχητικό μήνυμα
		self.lookup_table[self.station_index][int(evt.collaboration_content["alarm"])] = 0


	"""
	  Χειρίζεται τις εντολές διαχείρισης απο το κέντρο ελέγχου
	"""
	def handle_controller_request(self, evt):

		# Αν η εντολή αφορά τα LEDs ανανεώνει κατάλληλα τις μεταβλητές που καθορίζουν το
		# ρυθμό των LEDs
		if evt.request["cmd"] == "led_blinkig" :
			
			self.flash_blinking = not self.flash_blinking

			self.steps = 1 if self.flash_blinking else 5

		# Αν η εντολή αφορά τον έλεγχο ήχου, τότε μέσω της βιβλιοθήκης pygame αναπαράγεται το κατάλληλο
		# αρχείο ήχου
		if evt.request["cmd"] == "sound_testing" :
			
			pygame.mixer.pre_init(frequency = 16000, channels = 1) 
			pygame.init()
			pygame.mixer.init(frequency = 16000, channels = 1)
			pygame.mixer.music.load("sounds/bell.wav")
			pygame.mixer.music.play()
			while pygame.mixer.music.get_busy() == True:
				continue		
			pygame.quit()

"""
 Το βασικό σημείο απο το οποίο ξεκινά η εκτέλεση του προγράμματος
"""
if __name__ == "__main__":

	if len(sys.argv) != 2:
		print("\nUsage: python3 MonitoringStation.py [0|1|2|3]\n")
		sys.exit(0)

	logging.basicConfig(filename = 'monitoring_station.log', level = logging.INFO)

	
	# Μας ενδιαφέρουμε να γνωρίζουμε πότε ο χρήστης τερματίζει το πρόγραμμα μέσω Ctrl+C
	# ώστε να εκτελούμε την μέθοδο clean_up() που τερματίζει ομαλά την εκτέλεση της
	# GPIO βιβλιοθήκης
	try
		# Δημιουργούμε ένα αντικείμενο της κλάσης MonitoringStation που έχουμε υλοποιήσει και περιλαμβάνει
		# την λογική της ειδικής εφαρμογής που βασίζεται στην βιβλιοθήκη OpenMIC
		station = MonitoringStation(int(sys.argv[1]))

		# Ξεκινά η εκτέλεση της εφαρμογής
		station.start()

	except KeyboardInterrupt:
		station.clean_up()
		sys.exit(0)
