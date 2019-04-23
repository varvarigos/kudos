"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""

class OpenMICException(Exception):
    """Base class for exceptions in this module."""
    pass
 
class InvalidContext(OpenMICException):
    
    def __init__(self):
        self.message = 'Invalid context'

class UnknownCommunicationDriver(OpenMICException):

    def __init__(self, driver):
        self.message = "Unknown communication driver: %s"%(driver)


class InvalidCommunicationParameters(OpenMICException):

    def __init__(self, connection_parameters, driver):
        self.message = "Connection parameters:  %s , for communication driver: %s"%(connection_parameters, driver)
 