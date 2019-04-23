
"""
    Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
    License: GPL 3.0
    Athens March 2019
"""

class EventBase(object):

    def __init__(self):
        super(EventBase, self).__init__()



####################  INTERNAL FRAMEWORK EVENTS  #################### 


class CommunicationInterfaceResponse(EventBase):
   
    def __init__(self, response):
        super(CommunicationInterfaceResponse, self).__init__()
        self.response = response


class CommunicationInterfaceRequest(EventBase):
   
    def __init__(self, request):
        super(CommunicationInterfaceRequest, self).__init__()
        self.request = request


#####################################################################




####################  EVENTS FOR GENERIC AGENT & SERVER APPLICATIONS  ####################

class EventAgentConnected(EventBase):

    def __init__(self, agent_id, heartbeat = {}):
        super(EventAgentConnected, self).__init__()
        self.agent_id = agent_id
        self.heartbeat = heartbeat

    def __str__(self):
        return str("%s => agent_id: %s , heartbeat: %s"%(self.__class__.__name__, self.agent_id, self.heartbeat))


class EventAgentHeartBeat(EventBase):

    def __init__(self, agent_id, heartbeat):
        super(EventAgentHeartBeat, self).__init__()
        self.agent_id = agent_id
        self.heartbeat = heartbeat
  
    def __str__(self):
        return str("%s => agent_id: %s , heartbeat: %s"%(self.__class__.__name__, self.agent_id, self.heartbeat))


class EventAgentsDisconnected(EventBase):

    def __init__(self, agents_ids):
        super(EventAgentsDisconnected, self).__init__()
        self.agents_ids = agents_ids

    def __str__(self):
        return str("%s => agents_ids: %s"%(self.__class__.__name__, self.agents_ids))


class EventAgentResponse(EventBase):
   
    def __init__(self, agent_id, request_id, response):
        super(EventAgentResponse, self).__init__()
        self.agent_id = agent_id
        self.request_id = request_id
        self.response = response

    def __str__(self):
        return str("%s => agent_id: %s , request_id: %s, response: %s"%(self.__class__.__name__, self.agent_id, self.request_id, self.response))


class EventControllerRequest(EventBase):

    def __init__(self, agent_id, request_id, request):
        super(EventControllerRequest, self).__init__()
        self.agent_id = agent_id
        self.request_id = request_id
        self.request = request

    def __str__(self):
        return str("%s => agent_id: %s , request_id: %s, request: %s"%(self.__class__.__name__, self.agent_id, self.request_id, self.request))


class EventAvailableAgents(EventBase):

    def __init__(self, other_agents_ids):
        super(EventAvailableAgents, self).__init__()
        self.agents_ids = other_agents_ids

    def __str__(self):
        return str("%s => agents_ids: %s"%(self.__class__.__name__, self.agents_ids))


class EventAgentCollaboration(EventBase):

    def __init__(self, agent_id, sender_agent_id, collaboration_content):
        super(EventAgentCollaboration, self).__init__()
        self.agent_id = agent_id
        self.sender_agent_id = sender_agent_id
        self.collaboration_content = collaboration_content

    def __str__(self):
        return str("%s => agent_id: %s , sender_agent_id: %s, collaboration_content: %s"%(self.__class__.__name__, self.agent_id, self.sender_agent_id, self.collaboration_content))


class EventAgentGeneralMessage(EventBase):
   
    def __init__(self, agent_id, message):
        super(EventAgentGeneralMessage, self).__init__()
        self.agent_id = agent_id
        self.message = message

    def __str__(self):
        return str("%s => agent_id: %s , response: %s"%(self.__class__.__name__, self.agent_id, self.message))

#####################################################################
