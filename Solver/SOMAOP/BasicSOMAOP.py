import copy
import math
from abc import ABC
from Solver.SolverAbstract import Agent, Msg
from Simulator.SimulationComponents import ServiceProvider, ServiceRequester


## SOMAOP Messages ##

class SkillMessage(Msg):
    def __init__(self, sender_id, receiver_id, context):
        Msg.__init__(self, sender_id, receiver_id, context)

    def __str__(self):
        return "SkillMessage from " + str(self.sender_id) + " to " + str(self.receiver_id) + ": " + str \
            (self.context)


class DistanceMessage(Msg):
    def __init__(self, sender_id, receiver_id, context):
        Msg.__init__(self, sender_id, receiver_id, context)

    def __str__(self):
        return "DistanceMessage from " + str(self.sender_id) + " to " + str(self.receiver_id) + ": " + str \
            (self.context)


# RPA Offer Message
class RPAOfferMessage(Msg):
    def __init__(self, sender_id, receiver_id, context):
        Msg.__init__(self, sender_id, receiver_id, context)

    def __str__(self):
        return "RPAOfferMessage from " + str(self.sender) + " to " + str(self.receiver) + ": " + str \
            (self.information)


class SP(Agent, ABC):
    def __init__(self, simulation_entity: ServiceProvider, t_now, algorithm_version):
        Agent.__init__(self, simulation_entity=simulation_entity, t_now=t_now)
        # Provider Variables
        self.util_i = {}
        self.skill_set = simulation_entity.workload

        # Algorithm Results
        self.neighbor_locations = {}  # {neighbor_id: location}
        self.schedule = []
        self.algorithm_version = algorithm_version

        # provider xi Variables
        self.xi_size = 0  # the amount of variables i have
        self.current_xi = {}  # variable assignments {x_id:assignment}
        self.domain = []  # [all domain options]

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

    # 1 - calculate travel time by distance and speed
    def travel_time(self, start_location, end_location):
        return self.simulation_entity.travel_time(start_location, end_location)


class SR(Agent, ABC):
    def __init__(self, simulation_entity: ServiceRequester, t_now, bid_type, algorithm_version):
        Agent.__init__(self, simulation_entity=simulation_entity, t_now=t_now)

        self.util_j = {}  # {skill:{provider:utility}}
        self.bid_type = bid_type  # int index for bid type within an algorithm
        self.skills_needed = self.simulation_entity.skills_requirements
        self.max_time = self.simulation_entity.max_time
        self.terminated = {}  # {skill:T\F}
        self.algorithm_version = algorithm_version

        # neighbor variables
        self.neighbors = []  # all neighbors ids
        self.neighbors_by_skill = {}  # {skill: [provider_ids]}
        self.reset_neighbors_by_skill()

        # Algorithm results
        self.neighbor_arrival_times = {}

        # utility variables
        self.simulation_times_for_utility = {}
        self.reset_simulation_times_for_utility()

    # 1 - calculates final utility according to team_simulation_times_for_utility dict
    def final_utility(self, SP_view):
        """
        method that get the relevant SPs and return the final utility - calc by simulation entity
        :param SP_view:
        :return:
        """
        raise NotImplementedError

    # reset methods
    # initiates neighbors_by_skill dict
    def reset_neighbors_by_skill(self):
        for skill in self.skills_needed.keys():
            self.neighbors_by_skill[skill] = []

    # initiates simulation_times_for_utility dict
    def reset_simulation_times_for_utility(self):
        for skill in self.skills_needed.keys():
            self.simulation_times_for_utility[skill] = {}

    # utility methods
    def calculate_current_utility(self):
        self.simulation_entity.calculate_current_utility()

    def calculate_current_skill_cover(self):
        self.simulation_entity.calculate_current_skill_cover()

    def provider_require(self, provider):
        skills_in_common = [s for s in provider.skill_set if s in self.skills_needed]
        return provider.travel_time(start_location=provider.simulation_entity.location,
                                    end_location=self.simulation_entity.location) <= self.max_time \
               and len(skills_in_common) > 0
