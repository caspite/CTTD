import copy
import math
from abc import ABC
from Solver.SolverAbstract import Agent, Msg
from Simulator.SimulationComponents import ServiceProvider, ServiceRequester


## SOMAOP Messages ##

# from requester to provider - what skills he needs (list)
# from provider to requester - what skills he has + quality (dict)
class MsgSkills(Msg):
    def __init__(self, sender_id, receiver_id, context):
        Msg.__init__(self, sender=sender_id, receiver=receiver_id, information=context)

    def __str__(self):
        return "MsgSkills from " + str(self.sender) + " to " + str(self.receiver) + ": " + str(self.information)


# location of sender
class MsgLocationAndSpeed(Msg):
    def __init__(self, sender_id, receiver_id, context):
        Msg.__init__(self, sender=sender_id, receiver=receiver_id, information=context)

    def __str__(self):
        return "MsgLocation from " + str(self.sender) + " to " + str(self.receiver) + ": " + str(self.information)


# from requester to provider - time per skill he needs
class MsgWorkload(Msg):
    def __init__(self, sender_id, receiver_id, context):
        Msg.__init__(self, sender=sender_id, receiver=receiver_id, information=context)

    def __str__(self):
        return "MsgWorkload from " + str(self.sender_id) + " to " + str(self.receiver_id) + ": " + str(self.context)


class SP(Agent, ABC):
    def __init__(self, simulation_entity: ServiceProvider):
        Agent.__init__(self, simulation_entity=simulation_entity)
        # Provider Variables
        self.util_i = {}
        self.skill_set = None

        # Algorithm Results
        self.chosen_requester = None
        self.neighbor_distances = {}
        self.schedule = []

    def __str__(self):
        return "SP " + Agent.__str__(self)

    def reset_util_i(self):
        self.util_i = {}

    def send_skills_msg(self, requester_id):
        msg_skills = Msg.MsgSkills(sender_id=self.id_, receiver_id=requester_id, context=self.skill_set)
        self.mailer.send_msg(msg_skills)  # todo communication

    def send_location_msg(self, agent_id):
        msg_location = Msg.MsgLocationAndSpeed(sender_id=self._id,
                                               context=[copy.deepcopy(self.simulation_entity.location),
                                                        self.simulation_entity.speed],
                                               receiver_id=agent_id)
        self.mailer.send_msg(msg_location)  # todo communication


class SR(Agent, ABC):
    def __init__(self, simulation_entity: ServiceRequester, bid_type):
        Agent.__init__(self, simulation_entity=simulation_entity)

        self.util_j = {}  # {provider:{skill:utility}}
        self.bid_type = bid_type
        self.skills_needed = self.simulation_entity.skills_requirements
        self.skills_completed = {}
        self.reset_skills_completed()
        self.skills_completed_time_dict = {}
        self.reset_skills_completed_time_dict()
        self.terminated = {}  # {skill:T\F}

        # Algorithm results
        self.allocated_providers = {}  # {skill:[providers]}
        self.reset_allocated_providers()
        self.neighbor_arrival_times = {}

        # utility variables
        self.team_simulation_times_for_utility = {}
        self.reset_team_simulation_times_for_utility()

    # reset methods
    def reset(self):
        self.reset_termination()
        # self.reset_allocated_providers()
        self.reset_util_j()

    def reset_skills_completed(self):
        for skill in self.skills_needed.keys():
            self.skills_completed[skill] = 0

    def reset_skills_completed_time_dict(self):
        for skill in self.skills_needed.keys():
            self.skills_completed_time_dict[skill] = {}

    def reset_team_simulation_times_for_utility(self):
        for skill in self.skills_needed.keys():
            self.team_simulation_times_for_utility[skill] = {}

    def reset_util_j(self):
        self.util_j = {}
        for skill in self.skills_needed.keys():
            self.util_j[skill] = {}
            for provider in self.neighbors[skill]:
                self.util_j[skill][provider] = 0

    def reset_termination(self):
        self.terminated = {}
        for skill in self.skills_needed.keys():
            if len(self.neighbors[skill]) > 0:
                self.terminated[skill] = False

    def reset_allocated_providers(self):
        self.allocated_providers = {}
        for skill in self.skills_needed.keys():
            self.allocated_providers[skill] = {}

    # Msg methods
    def send_skills_msg(self, provider_id, time_per_skill_unit):
        msg_skills = Msg.MsgSkills(sender_id=self._id, receiver_id=provider_id, context=copy.deepcopy(self.skills_needed))
        self.mailer.send_msg(msg_skills)  # todo add communication
        msg_workload = Msg.MsgWorkload(sender_id=self.id_, receiver_id=provider_id,
                                           context=time_per_skill_unit)
        self.mailer.send_msg(msg_workload)  # todo add communication

    def send_location_msg(self, agent_id):
        msg_location = Msg.MsgLocation(sender_id=self._id, context=copy.deepcopy(self.simulation_entity.location),
                                           receiver_id=agent_id)
        self.mailer.send_msg(msg_location)  # todo add communication
