"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""

import time
import pygame

from PyQt5.QtCore import QThread

class StationSounds(QThread):

	def __init__(self):
		
		QThread.__init__(self)
		self.sound_file_name = None
		self.play_sound = False

	def __del__(self):
		
		self.wait()


	def on_play_sound(self, file_name):
		
		self.play_sound = False
		self.sound_file_name = "sounds/%s.wav"%(file_name)
		self.play_sound = True
		print(self.sound_file_name)

	def run(self):

		pygame.mixer.pre_init(frequency = 16000, channels = 1) 

		pygame.init()

		while True:

			if self.play_sound :

				pygame.mixer.init(frequency = 16000, channels = 1)
				pygame.mixer.music.load(self.sound_file_name)
				pygame.mixer.music.play()

				while pygame.mixer.music.get_busy() == True:
					continue
 

			time.sleep(1)
			
		pygame.quit()
