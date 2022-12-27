from abc import ABC
import copy

from Solver.SOMAOP.BasicSOMAOP import *


class RpaSR(SR):
    def __init__(self, simulation_entity: ServiceRequester, bid_type, t_now=None, algo_version=0):
        if t_now is None: t_now = simulation_entity.last_time_updated
        SR.__init__(self, simulation_entity=simulation_entity, bid_type=bid_type, t_now=t_now, algorithm_version=algo_version)

        self.offers_received_by_skill = {}
        self.reset_offers_received_by_skill()
        self.allocated_offers = {}
        self.offers_to_send = []
        self.current_utility = 0

    # 1 - reset fields of algorithm
    def reset_offers_received_by_skill(self):
        for skill in self.skills_needed:
            self.offers_received_by_skill[skill] = []

    def reset_allocated_offers(self):
        for skill in self.skills_needed:
            self.allocated_offers[skill] = set()

    # 2 - algorithm compute (single agent response to iteration)
    def compute(self):
        # self.reset_allocated_offers()

        # gives them utility 0
        self.update_unfeasible_offers_unallocated()
        self.allocate_offers()
        self.update_utilities()

    def allocate_offers(self):
        skills_needed_temp = copy.deepcopy(self.skills_needed)

        self.allocated_offers, self.NCLO = self.simulation_entity.allocated_offers(skills_needed_temp,
                                                                        self.offers_received_by_skill)
        self.reset_offers_received_by_skill()

    def update_utilities(self):
        for skill in self.allocated_offers:
            for offer in self.allocated_offers[skill]:
                offer.utility = self.simulation_entity.calc_utility_to_offer(skill, offer, self.bid_type)
                self.offers_to_send.append(offer)

    def update_unfeasible_offers_unallocated(self):
        unallocated = []
        for skill in self.offers_received_by_skill:
            for offer in self.offers_received_by_skill[skill]:
                if offer.arrival_time > self.max_time or offer.amount is 0:
                    unallocated.append(offer)
                    self.offers_to_send.append(offer)
        update_unallocated(unallocated)

    # 3 - after computation broadcast information to neighbors
    def send_msgs(self):
        while self.offers_to_send:
            offer = self.offers_to_send.pop(0)
            msg_offer = RPAOfferMessage(self._id, offer.provider, offer)
            self.mailer.send_msg(msg_offer)

    # 4 - receive incoming information from neighbors
    def agent_receive_a_single_msg(self, msg):
        if isinstance(msg, RPAOfferMessage):
            offer = msg.information
            self.offers_received_by_skill[offer.skill].append(offer)

    def initialize(self):
        pass

    def get_utility_by_SP_view(self, SP_view):
        allocated_offers = copy.deepcopy(self.allocated_offers)
        return self.simulation_entity.final_utility(allocated_offers, SP_view)




# when offer is unfeasibly - the utility is 0 and the amount needed is 0
def update_unallocated(offers):
    for offer in offers:
        offer.utility = 0
        offer.amount = 0


class RpaSP(SP):
    def __init__(self, simulation_entity: ServiceProvider, t_now=None, algo_version=0):
        if t_now is None: t_now = simulation_entity.last_time_updated
        SP.__init__(self, simulation_entity=simulation_entity, t_now=t_now, algorithm_version=algo_version)

        self.offers_received = []
        self.response_offers = []

    def initialize(self):
        for offer in self.domain:
            to_offer = copy.deepcopy(offer)
            travel_time = round(self.travel_time(self.location, to_offer.location), 2)
            to_offer.arrival_time = travel_time
            to_offer.amount = self.skill_set[to_offer.skill]
            self.response_offers.append(to_offer)

    # 3 - algorithm compute (single agent response to iteration)
    def compute(self):
        self.response_offers = []
        self.current_xi = {}
        self.accept_offers()
        self.offers_received = []

    def accept_offers(self):
        self.NCLO, self.current_xi, self.response_offers = self.simulation_entity.accept_offers(self.offers_received)

    # 4 - after computation broadcast information to neighbors
    def send_msgs(self):
        while self.response_offers:
            offer = self.response_offers.pop(0)
            msg_availability = RPAOfferMessage(self._id, offer.requester, offer)
            self.mailer.send_msg(msg_availability)

    # 5 - receive incoming information from neighbors
    def agent_receive_a_single_msg(self, msg):
        if isinstance(msg, RPAOfferMessage):
            self.offers_received.append(msg.information)