
from distutils.core import setup

setup(
	name = 'OpenMIC',
	version = '1.0',
	description = 'OpenMIC - Open Multi-Agent Intelligence and Computing',
	author = 'Andreas varvarigos, Anastasis Varvarigos',
	author_email = 'https://github.com/varvarigos/kudos',
	url = 'https://github.com/varvarigos/kudos',
	packages = [ 
		'openmic', 
		'openmic.agent', 
		'openmic.controller', 
		'openmic.drivers', 
		'openmic.utils',
		'openmic.lib' 
	],
	install_requires=[
		'psutil>=5.4.6',
		'pika>=1.0.0',
		'pyzmq>=17.0.0'
	]
)
