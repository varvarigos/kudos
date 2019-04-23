"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""


from multiprocessing import Lock, Queue, queues


class SyncQueue(queues.Queue):
        
    def __init__(self):
        self.q = Queue()
        self.lock = Lock()

    def add(self, item):
        self.lock.acquire()
        self.q.put(item)
        self.lock.release()

    def get(self):
        return self.q.get()
