"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""

import time
import pygame

from PyQt5.QtCore import QThread

"""
   H κλάση παρέχει το μηχανισμό για την αναπαραγωγή ενός αρχείου ήχου. 
"""

class StationSounds(QThread):

	def __init__(self):
		
		QThread.__init__(self)
		self.sound_file_name = None
		self.play_sound = False

	def __del__(self):
		
		self.wait()


	"""
	   Η μεθοδος μας επιτρέπει να ορίσουμε το αρχείο ήχου που θα αναπαραχθεί μέσω της 
	   μεθόδου run()
	"""
	def on_play_sound(self, file_name):
		
		self.play_sound = False
		self.sound_file_name = "sounds/%s.wav"%(file_name)
		self.play_sound = True
		print(self.sound_file_name)

	"""
	   Είναι η βασική μέθοδος που τρέχει διαρκώς και ανάλογα με την τιμή που έχει η μεταβλητή play_sound 
	   αρχίζει την αναπαραγωγή του αρχείου ήχου που περιέχει η μεταβλητή sound_file_name
	   Επιλέξαμε αυτό την οργανωση γιατι θέλουμε το μηνυμα εκκενωσης να ακουγεται συνεχως σε περίπτωση 
	   κάποιας έκτακτης ανάγκης.
	"""
	def run(self):

		# Οι επόμενες δύο εντολές αρχικοποιούν την βιβλιοθήκη pygame μέσω της οποίας 
		# γίνεται η αναπαραγωγή των αρχείων ήχου
		pygame.mixer.pre_init(frequency = 16000, channels = 1) 

		pygame.init()

		while True:

			# Αν η μεταβλητη είναι True τότε αρχίζει την αναπαραγωγή του αρχείου
			if self.play_sound :   

				#οριζουμε τις παραμετρους, το αρχείο και αρχίζουμε την αναπαραγωγή
				pygame.mixer.init(frequency = 16000, channels = 1)
				pygame.mixer.music.load(self.sound_file_name)
				pygame.mixer.music.play()

				#περιμενουμε μεχρι να τελειωσει η τρεχουσα αναπαραγωγη
				while pygame.mixer.music.get_busy() == True:
					continue
 

			time.sleep(1)
			
		pygame.quit()
