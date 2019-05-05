
"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""

import time
import json
import logging

import agent_operations

import openmic.lib.events as events
import openmic.lib.constants as constants
import openmic.utils.connection_parameters as cons
import openmic.agent.agent_context as agent_context
import openmic.agent.agent_instance as agent_instance


class RaspberryAgent:


	def __init__(self) :
 
		self.panding_requests = {}

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
		#rabbitmq_params = cons.RabbitMQParameters("","", "", virtual_host = "")
		#self.context = agent_context.AgentContext(rabbitmq_params, constants.DRIVER_RABBITMQ)
		

	def start(self):

		# Δημιουργούμε το αντικείμενο της βασικής κλάσης AgentInstance που παρέχει τις λειτουργίες της
		# βιβλιοθήκης OpenMIC στην εφαρμογή μας
		self.agent_instance = agent_instance.AgentInstance(self.context) 

		# Μας ενδιαφέρει μόνο να παρακολουθούμε για μηνύματα με εντολές απο την εφαρμογή ελέγχου και διαχείρισης,
		# έτσι κάναμε εγγραφή μονο για αυτό το event και ορίσαμε οτι τα σχετικά events θέλουμε
		# να τα χειρίζεται η μέθοδος handle_controller_request
		self.context.connect([events.EventControllerRequest], self.handle_controller_request)


	# Χειρίζεται τα μηνύματα με τις εντολές, εκτελεί τις κατάλληλες ενέργειες και επιστρέφει τα αποτελέσματα
	def handle_controller_request(self, evt):

		request = evt.request

		# Ελέγχουμε το πεδιο "cmd" αφού αυτό καθορίζει το είδος της εντολής, άρα και τις ενέργειες 
		# που πρέπει να εκτελεστούν, σε κάθε περίπτωση χρησιμοποιούμε την κατάλληλη μέθοδο 
		# απο το αρχείο agent_operations.py
		
		# Εντολή καταγραφής
		if request["cmd"] == "inventory" :

			if len(request["params"]) == 0 :
				params = 2
			else:
				params = int(request["params"])

			response = agent_operations.inventory(params)
		
		# Εκτέλεση εντολής συστήματος
		if request["cmd"] == "shell_command" :
			response = agent_operations.execute_shell_command(request["params"])

		# Εκτέλεση γενικής εντολής
		if request["cmd"] == "simple_command" :
			response = agent_operations.execute_simple_command(request["params"])

		# Εγκατάσταση πακέτου λογισμικού
		if request["cmd"] == "install_package" :
			response = agent_operations.install_package(request["params"])

		# Απεγκατάσταση πακέτου λογισμικού
		if request["cmd"] == "uninstall_package" :
			response = agent_operations.uninstall_package(request["params"])

		# Στο τελικό βήμα επιστρέφουμε μέσω της κατάλληλης μεθόδου της βιβλιοθήκης OpenMIC
		# το αποτέλεσμα της εντολής προς την εφαρμογή ελέγχου και διαχείρισης
		self.agent_instance.send_response(evt.request_id, response)
		
"""
 Το βασικό σημείο απο το οποίο ξεκινά η εκτέλεση του προγράμματος
"""
if __name__ == "__main__":

	logging.basicConfig(filename = 'agent.log', level = logging.INFO)

	# Δημιουργούμε ένα αντικείμενο της κλάσης RaspberryAgent που έχουμε υλοποιήσει και περιλαμβάνει
	# την λογική της ειδικής εφαρμογής που βασίζεται στην βιβλιοθήκη OpenMIC
	agent = RaspberryAgent()

	# Ξεκινά η εκτέλεση της ειδικής εφαρμογής 
	agent.start()
