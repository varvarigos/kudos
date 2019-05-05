
"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""

import sys
import json
import logging

import DataModel
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


"""
  Η βασική κλάση κληρονομεί απο την κλάση QMainWindow της βιβλιοθήκης PyQt5 καθως περιλαμβάνει τόσο την 
  υλοποίηση της λογικής της εφαρμογής όσο και της γραφικής διεπαφής.
  
  Ο σχεδιασμός της γραφικής διεπαφής (ui/MainWindow.ui) έγινε με την βοήθεια του διαθέσιμου εργαλείου Qt Designer 
  ενώ για την δημιουργία του σχετικού κώδικα (MainWindow.py) χρησιμοποιήσαμε την εντολή pyuic5.
  
"""
class RaspberryController(QMainWindow, MainWindow.Ui_MainWindow):

	# Ορίζουμε 3 βοηθητικά signals χρησιμοποιώντας την βιβλιοθήκη PyQt5, αφορούν αποκλειστικά
	# λειτουργίες που σχετίζονται με την λειτουργία της γραφικής διεπαφής
	agent_response_signal = pyqtSignal(events.EventAgentResponse)
	agent_heartbeat_signal = pyqtSignal(events.EventAgentHeartBeat)
	agents_disconnected_signal = pyqtSignal(events.EventAgentsDisconnected)

	def __init__(self):
	
		super(RaspberryController, self).__init__()

		self.instance = None

		self.setupUi(self)

		self.setup_actions()

		self.setup_openmic_controller()

		self.data_model = DataModel.DataModel(self.agentsComboBox, self.tasksComboBox, self.showTaskAgentsComboBox)

		self.initialize_ui()

		self.show()



	"""
	   Η παρακάτω μέθοδος χρησιμοποιεί τον μηχανισμό χειρισμού γεγονότων σε στοιχεία της γραφικής
	   διεπαφής της PyQt5 για να ορίσει τις μεθόδους που εκτελούν τις αντίστοιχες ενέργειες.
	   Πρόκειται για ενέργειες που σχετίζονται με την γραφική διεπαφή και την βιβλιοθήκη PyQt5 και οχι
	   με την βιβλιοθήκη OpenMIC.
	"""
	def setup_actions(self):

		# Menu action
		self.actionAbout.triggered.connect(self.credentials)

		# Actions για τα 4 κεντρικά buttons
		self.agentsButton.clicked.connect(self.agents_page)
		self.createTaskButton.clicked.connect(self.create_task_page)
		self.tasksButton.clicked.connect(self.tasks_page)
		self.resultsButton.clicked.connect(self.results_page)
		
		# Αctions για τα combobox της εφαρμογής
		self.agentsComboBox.currentIndexChanged[int].connect(self.show_agent_details)
		self.tasksComboBox.currentIndexChanged[int].connect(self.show_tasks)
		self.taskCategoryComboBox.currentIndexChanged[int].connect(self.update_task_form)
		self.resultsComboBox.currentIndexChanged[int].connect(self.show_results)

		# Actions για τα buttons 
		self.saveTaskButton.clicked.connect(self.save_task)
		self.clearTaskButton.clicked.connect(self.clear_task)
		self.deleteTaskButton.clicked.connect(self.delete_task)
		self.executeTaskButton.clicked.connect(self.execute_task)
		self.execute2AllButton.clicked.connect(self.execute_to_all)


	 
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
		context.connect([events.EventAgentResponse], self.agent_response)
		
		# Συσχετίζουμε τα 3 βοηθητικά signals που ορίσαμε στην αρχή της κλάσεις με τις
		# μεθόδους που τα χειρίζονται
		self.agent_response_signal.connect(self.handle_response_signal)
		self.agent_heartbeat_signal.connect(self.handle_heartbeat_signal)
		self.agents_disconnected_signal.connect(self.handle_disconnected_signal)
	
 
	"""
	  Εμφανίζει το παράθυρο με τις πληροφορίες σχετικά με την εφαρμογή
	"""
	def credentials(self):

		message = '<b>Ανδρέας Βαρβαρίγος & Αναστάσης Βαρβαρίγος 2019</b><br><br>'
		message += '<a href="https://github.com/varvarigos/kudos">https://github.com/varvarigos/kudos</a><br>'
		message += '<div>Icons made by <a href="https://www.flaticon.com/authors/smashicons" title="Smashicons">Smashicons</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>'
		message += '<div>Icons made by <a href="https://www.flaticon.com/authors/vectors-market" title="Vectors Market">Vectors Market</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>'
		message += '<div>Icons made by <a href="https://www.freepik.com/" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>'
		message += '<div>Icons made by <a href="https://www.flaticon.com/authors/surang" title="surang">surang</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>'
		message += '<div>Icons made by <a href="https://www.flaticon.com/authors/dave-gandy" title="Dave Gandy">Dave Gandy</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>'

		dlg = QMessageBox(self)
		dlg.setText(message)
		dlg.setIcon(QMessageBox.Information)
		dlg.show()

	"""
	  Αρχικοποιεί την γραφική διεπαφή κατά την έναρξη της εκτέλεσης της εφαρμογής
	"""
	def initialize_ui(self):

		self.stackedWidget.setCurrentIndex(0)
		self.tabWidget.setCurrentIndex(0)
		self.taskParameterEdit.setEnabled(False)

		# Ορίζουμε να είναι διαθέσιμες πάντα απο μια εργασια καταγραφής για κάθε ένα απο τους 3 υποστηριζόμενους τύπους 
		self.data_model.create_task(0, "Χαρακτηριστικά", "0")
		self.data_model.create_task(1, "Πακέτα λογισμικού", "1")
		self.data_model.create_task(2, "Πλήρης καταγραφή", "2")


	"""
	  Εμφανίζει στην γραφική διεπαφή την σελίδα που παρουσιάζει τις πληροφορίες για τις διαθέσιμες συσκευές
	"""
	def agents_page(self):
		
		self.stackedWidget.setCurrentIndex(0)
		self.tabWidget.setCurrentIndex(0)
		self.show_agent_details(self.agentsComboBox.currentIndex())


	"""
	  Εμφανίζει στην γραφική διεπαφή την σελίδα που επιτρέπει στους χρήστες να δημιουργούν νέες εργασίες
	"""
	def create_task_page(self):
		
		self.stackedWidget.setCurrentIndex(1)

	"""
	  Εμφανίζει στην γραφική διεπαφή την σελίδα που παρουσιάζει τις διαθέσιμες προς εκτέλεση εργασίες
	"""
	def tasks_page(self):
		
		self.stackedWidget.setCurrentIndex(2)

	"""
	  Εμφανίζει στην γραφική διεπαφή την σελίδα που παρουσιάζει τις εργασίες που έχουν εκτελεστεί
	"""
	def results_page(self):
		
		self.stackedWidget.setCurrentIndex(3)

		
	"""
	  Εμφανίζει στις δυο καρτέλες της αρχικής σελίδας της λεπτομέρειες κατάστασης και τα διαθέσιμα
	  πακέτα λογισμικού για κάποια συγκεκριμένη συσκευή
	"""	
	def show_agent_details(self, index):

		if index == - 1:
			return

		agent_id = self.agentsComboBox.itemData(index)

		self.hardwarePlainTextEdit.setPlainText(self.data_model.get_agent_hardware(agent_id))
		self.softwarePlainTextEdit.setPlainText(self.data_model.get_agent_software(agent_id))

	"""
	   Καθορίζει τις πληροφορίες που περιέχονται στην σελίδα με τις διαθέσιμες προς εκτέλεση εργασίες
	"""
	def show_tasks(self, index):

		if index == -1:
			return

		task = self.data_model.get_task(index)

		category_name = self.taskCategoryComboBox.itemText(task.category)

		self.showTaskCategoryEdit.setText(category_name)

		if task.category > 2 :
			self.showTaskParametersEdit.setEnabled(True)
			self.showTaskParametersEdit.setText(task.parameters)
		else:
			self.showTaskParametersEdit.setEnabled(False)
			self.showTaskParametersEdit.setText("")

	"""
	   Καθορίζει τις πληροφορίες που περιέχονται στην σελίδα με τις διαθέσιμες προς εκτέλεση εργασίες
	"""
	def show_results(self, index):
		
		if index != -1:
			self.resultsTextEdit.clear()
			results = self.data_model.get_task_results(self.resultsComboBox.itemData(index))
			if results != None :
				self.taskStatusLabel.setText("Ολοκληρωμένη.")
				self.resultsTextEdit.setPlainText(str(results))
			else:
				self.taskStatusLabel.setText("Εκκρεμής")

	"""
	   Χειρίζεται τα πεδία που έχει η φόρμα δημιουργίας νέων εργασιών
	"""
	def update_task_form(self, index):
		
		if index > 2 :
			self.taskParameterEdit.setEnabled(True)
		else:
			self.taskParameterEdit.clear()
			self.taskParameterEdit.setEnabled(False)

	"""
	   Διαγράφει μια εργασία
	"""
	def delete_task(self):

		index = self.tasksComboBox.currentIndex()

		if index != -1 :
			self.data_model.delete_task(index)
			self.showTaskParametersEdit.clear()
			self.showTaskCategoryEdit.clear()

	"""
	   Στέλνει μια εργασία προς εκτέλεση σε κάποια συγκεκριμένη συσκευή
	"""
	def execute_task(self):
		
		task_index = self.tasksComboBox.currentIndex()
		agent_index = self.showTaskAgentsComboBox.currentIndex()

		if task_index == -1 or agent_index == -1:
			self.information_message("Δεν μπορεί να εκτελεστεί η εργασία με τις συγκεκριμένες επιλογές.")
			return

		task = self.data_model.submit_task(task_index)

		ids = self.instance.submit_request_to_agents(task.agent_request, [self.showTaskAgentsComboBox.itemData(agent_index)])

		self.data_model.map_task_to_results(task, ids[0])

		self.resultsComboBox.addItem("%s-%s"%(task.task_name,task.timestamp), ids[0])

	"""
	   Στέλνει μια εργασία προς εκτέλεση σε όλες τις διαθέσιμες συσκευές
	"""
	def execute_to_all(self):

		task_index = self.tasksComboBox.currentIndex()

		if task_index == -1 :
			self.information_message("Δεν μπορεί να εκτελεστεί η εργασία με τις συγκεκριμένες επιλογές.")
			return

		task = self.data_model.submit_task(task_index)

		agents_ids = list(self.data_model.agents.keys())

		ids = self.instance.submit_request_to_agents(task.agent_request, agents_ids)

		for ti in ids:
			self.data_model.map_task_to_results(task, ti)
			self.resultsComboBox.addItem("%s-%s"%(task.task_name,task.timestamp), ti)

	"""
	   Δημιουργεί μια νέα εργασία
	"""
	def save_task(self):

		name = self.taskNameEdit.text()
		parameters = self.taskParameterEdit.text()
		category = self.taskCategoryComboBox.currentIndex()

		if len(name) == 0:
			self.information_message("Δεν έχετε ορίσει όνομα για την νέα εργασία.")
			return

		if  category > 2 and len(parameters) == 0: 
			self.information_message("Δεν έχετε ορίσει την περιγραφή της νέας εργασίας.")
			return
		
		if category < 2 :
			parameters = str(category)

		self.data_model.create_task(category, name, parameters)
		self.clear_task()


	"""
	   Καθαρίζει την φόρμα δημιουργίας μιας εργασίας
	"""
	def clear_task(self):
		
		self.taskNameEdit.clear()
		self.taskParameterEdit.clear()
		self.taskCategoryComboBox.setCurrentIndex(0)

	"""
	  Ανανεώνει τις εσωτερικές πληροφορίες που διατηρεί και την γραφική διεπαφή στην περίπτωση που
	  χαθεί η επικοινωνία με κάποια συσκευή
	"""
	def handle_disconnected_signal(self, evt):
		
		names = []
		
		self.data_model.handle_agent_disconnection(evt)
		
		for agent_id in evt.agents_ids:
			names.append(self.data_model.get_agent(agent_id).name)
		
		self.critical_message("Απώλεια επικοινωνίας με τις συσκευές: %s"%(" , ".join(names)))
	
	"""
	  Ανανεώνει τις εσωτερικές πληροφορίες που διατηρεί και την γραφική διεπαφή κάθε φορά που
	  λαμβάνει ένα μήνυμα κατάστασης απο κάποια συσκεύη
	"""
	def handle_heartbeat_signal(self, evt):
		
		self.data_model.handle_agent_data(evt)

	"""
	  Ανανεώνει τις εσωτερικές πληροφορίες που διατηρεί και την γραφική διεπαφή όταν λάβει την απάντηση για κάποια
	  εργασία που στάλθηκε προς εκτέλεση
	"""
	def handle_response_signal(self, evt):

		update_agent_response = self.data_model.handle_agent_response(evt)

		if update_agent_response :
			self.show_agent_details(self.agentsComboBox.currentIndex())

		if evt.request_id in list(self.data_model.task_results.keys()):
			self.show_results(0)
	
	"""
	   Χειρίζεται events απο την βιβλιοθήκη OpenMIC σχετικά με την αναγνώριση σύνδεσης μιας συσκευής
	"""
	def agent_connect(self, evt):
		
		# Ανανεώνει τις πληροφορίες που διατηρεί μέσω της DataModel
		self.data_model.handle_agent_data(evt)
	
		# Αν πρόκειται για την πρώτη σύνδεση τοτε αυτόματα στέλνει μέσω της βιβλιοθήκης
		# OpenMIC μια εντολή προς αυτή ώστε να εκτελεστεί μια πλήρης καταγραφή των χαρακτηριστικών της 
		if self.data_model.get_agent(evt.agent_id).newly_discovered :
			self.instance.submit_request_to_agents(json.dumps({ "cmd": "inventory", "params": "2" }), [evt.agent_id])
	
	"""
	  Χειρίζεται events απο την βιβλιοθήκη OpenMIC σχετικά με την απώλεια επικοινωνίας απο συσκευές
	"""
	def agent_disconnect(self, evt):

		self.agents_disconnected_signal.emit(evt)
	
	"""
	  Χειρίζεται events απο την βιβλιοθήκη OpenMIC σχετικά με μηνύματα κατάστασης από κάποια συσκευή
	"""
	def agent_heartbeat(self, evt):
	
		self.agent_heartbeat_signal.emit(evt)
	
	"""
	  Χειρίζεται events απο την βιβλιοθήκη OpenMIC σχετικά με το αποτέλεσμα κάποιας εντολής
	"""
	def agent_response(self, evt):
	
		self.agent_response_signal.emit(evt)


	def critical_message(self, msg):
		
		dlg = QMessageBox(self)
		dlg.setText(msg)
		dlg.setIcon(QMessageBox.Critical)
		dlg.show()


	def information_message(self, msg):
		
		dlg = QMessageBox(self)
		dlg.setText(msg)
		dlg.setIcon(QMessageBox.Information)
		dlg.show()


"""
 Το βασικό σημείο απο το οποίο ξεκινά η εκτέλεση του προγράμματος
"""
if __name__ == '__main__':

	logging.basicConfig(filename = 'raspberries_controller.log', level = logging.INFO)

	app = QApplication(sys.argv)	
	app.setApplicationName("Raspberries Remote Management")
	
	# Δημιουργούμε ένα αντικείμενο της κλάσης RaspberryController που έχουμε υλοποιήσει και περιλαμβάνει
	# την γραφική διεπαφή (βασίζεται στη βιβλιοθήκη PyQt5) και τη λογική της εφαρμογής ελέγχου και διαχείρισης (βασίζεται 
	# στην βιβλιοθήκη OpenMIC
	window = RaspberryController()

	app.exec_()

