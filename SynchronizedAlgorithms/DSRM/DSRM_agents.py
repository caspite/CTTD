from Solver.SOMAOP.BasicSOMAOP import *
from SynchronizedAlgorithms.SynchronizedSolver import VariableAssignment
import enum

class ProviderStatus(enum.Enum):
    at_request = 1
    in_transport = 2

class DsrmSP(SP):
    def __init__(self, simulation_entity: ServiceProvider, t_now=None, algo_version=0):
        if t_now is None: t_now = simulation_entity.last_time_updated
        SP.__init__(self, simulation_entity=simulation_entity, t_now=t_now, algorithm_version=algo_version)

        # all rounds GS variables
        self.chosen_requester = None

        # single round GS variables
        self.play_round = True
        self.offers_received = []

        #  simulation variables
        self.status = ProviderStatus.in_transport
        self.last_update_time = 0
        self.current_service = None
    # --------------------GS ALGORITHM PRE-PROCESSING RELATED METHODS--------------------------
    def reset_for_DSRM(self):
        self.chosen_requester = None

    def initialize(self):
        # so that the SP doesn't take part in the GS when it has already chosen before this round
        if self.chosen_requester is not None:
            self.play_round = False
        else:
            self.play_round = True

        if self.play_round:
            self.util_i = {}
            self.send_service_proposal_msg()

    def compute(self):
        if self.play_round:
            if self.offers_received:
                best_choice = self.compute_GS_response()
                self.send_GS_responses(best_choice)
                self.chosen_requester = copy.deepcopy(best_choice)
                self.offers_received = []

    def send_GS_responses(self, best_choice):
        for sr in self.neighbors:
            msg = GSResponseMsg(self._id, sr, copy.deepcopy(best_choice))
            self.mailer.send_msg(msg)

    def compute_GS_response(self):
        utilities_for_options = {}
        if self.chosen_requester is not None:
            utilities_for_options[self.chosen_requester] = self.util_i[self.chosen_requester[0]][
                self.chosen_requester[1]]

        for offer_received in self.offers_received:
            utilities_for_options[offer_received] = self.util_i[offer_received[0]][offer_received[1]]

        # NCLO
        self.NCLO += Agent.number_of_comparisons(1, len(utilities_for_options))

        max_offer = max(utilities_for_options, key=utilities_for_options.get)
        return max_offer  # requester, skill tuple that provider wants to be sent to
    def send_service_proposal_msg(self):
        for requester in self.neighbors:

            skills = copy.deepcopy(self.skill_set)
            for skill in skills.keys():
                offer = VariableAssignment(self.getId(), requester, skill,
                                            copy.deepcopy(self.neighbor_locations[requester]))
                if isinstance(self.simulation_entity, MedicalUnit):
                    offer.max_capacity = copy.deepcopy(self.simulation_entity.get_max_capacity())
                travel_time = round(self.travel_time(self.location, self.neighbor_locations[requester]), 2)
                offer.arrival_time = travel_time
                offer.amount = self.skill_set[skill]
                msg_value = ServiceProposalMsg(sender_id=self._id, receiver_id=requester,
                                        context=offer)
                self.mailer.send_msg(msg_value)


    # --------------------SIMULATION RELATED METHODS--------------------------
    def arrive_to_requester(self, current_time):
        self.status = ProviderStatus.at_requester

        self.update_location(current_time)

        self.last_update_time = current_time

    def leave_requester(self, current_time):
        self.status = ProviderStatus.in_transport

        # also updates last update time
        self.update_skill_usage(current_time)

        self.current_service = None

    def update_skill_usage(self, current_time):
        if self.current_service is not None and self.current_service.arrival_time < current_time:  # provider has already arrived
            skill_usage = int(round(current_time - self.last_update_time, 2) / \
                              self.work_time_i[self.current_service.requester][self.current_service.skill])

            self.skill_set[self.current_service.skill] -= skill_usage

            # todo - remove
            if self.skill_set[self.current_service.skill] < 0:
                raise Exception("Used Too many Skills")

            if self.skill_set[self.current_service.skill] == 0:
                del self.skill_set[self.current_service.skill]

            self.last_update_time += self.work_time_i[self.current_service.requester][
                                         self.current_service.skill] * skill_usage

    def update_location(self, current_time):
        if self.current_service is not None:
            arrival_location = self.current_service.location

            if self.status == ProviderStatus.at_requester:
                self.current_location = arrival_location

            elif self.status == ProviderStatus.in_transport:
                if self.current_location[0] == self.current_service.location[0] and \
                        self.current_location[1] == self.current_service.location[1]:
                    return

                time_travel_begin = self.find_leaving_time()

                if time_travel_begin == current_time:  # just left
                    return

                ratio = find_ratio_of_travel_complete(time_travel_begin=time_travel_begin,
                                                      arrival_time=self.current_service.arrival_time,
                                                      current_time=current_time)
                x_dist_ratio = abs((arrival_location[0] - self.current_location[0])) * ratio
                y_dist_ratio = abs((arrival_location[1] - self.current_location[1])) * ratio

                current_location = []

                if self.current_location[0] < arrival_location[0]:
                    current_location.append(round(self.current_location[0] + x_dist_ratio, 2))
                else:
                    current_location.append(round(self.current_location[0] - x_dist_ratio, 2))

                if self.current_location[1] < arrival_location[1]:
                    current_location.append(round(self.current_location[1] + y_dist_ratio, 2))
                else:
                    current_location.append(round(self.current_location[1] - y_dist_ratio, 2))

                self.current_location = current_location

    def find_leaving_time(self):
        arrival_location = self.current_service.location
        arrival_time = self.current_service.arrival_time

        x_dist_total = abs((arrival_location[0] - self.current_location[0]))
        y_dist_total = abs((arrival_location[1] - self.current_location[1]))

        horizontal_dist_total = (x_dist_total ** 2 + y_dist_total ** 2) ** 0.5

        time_travel_begin = round(arrival_time - (horizontal_dist_total / self.travel_speed), 2)

        return time_travel_begin

    def agent_receive_a_single_msg(self, msg):
        pass
    def send_msgs(self):
        pass

class DsrmSR(SR):
    def __init__(self,simulation_entity: ServiceRequester, bid_type, t_now=None, algo_version=0):
        if t_now is None: t_now = simulation_entity.last_time_updated
        SR.__init__(self, simulation_entity=simulation_entity, bid_type=bid_type, t_now=t_now,
                        algorithm_version=algo_version)

        self.allocated_offers = {}
        self.offers_to_send = []
        self.current_utility = 0
        self.time_per_skill_unit = {}
        self.temp_simulation_entity = copy.deepcopy(simulation_entity)


        # ---- multiple round GS variables
        self.GS_accepted_providers_utility = {}
        self.all_round_neighbor_skills = {}
        # ---- single round GS variables
        # SPs that have currently approved my offer {skill: [sp id]}
        self.GS_accepted_providers = {}
        # SPs i sent offer to {skill: [sp id]}
        self.GS_has_offered = {}
        self.GS_has_not_offered = {}
        # responses received from SPs {sp id: (chosen sr id, skill)}
        self.GS_SP_choices = {}
        # skills that have terminated {skill: t\f}


        # ---- simulation variables
        self.sim_temp_temp_skills_needed = copy.deepcopy(self.skills_needed)
        self.sim_temp_max_required = copy.deepcopy(self.simulation_entity.max_required)

        self.current_services = []  # [variable assignments]
        self.working_by_skill = {}
        self.amount_working = {}  # {skill:amount}
        self.neighbors_skill = {} # {neighbor id: {skill:workload}}
   # --------------------GS ALGORITHM PRE-PROCESSING RELATED METHODS--------------------------
    def reset_for_DSRM(self):
        self.reset_GS_accepted_providers()
        self.reset_GS_accepted_providers_utility()
        self.all_round_neighbor_skills = {}

    def reset_GS_accepted_providers(self):
        self.GS_accepted_providers = {}
        for skill in self.sim_temp_temp_skills_needed:
            self.GS_accepted_providers[skill] = set()

    def reset_GS_accepted_providers_utility(self):
        self.GS_accepted_providers_utility = {}
        for skill in self.sim_temp_temp_skills_needed:
            self.GS_accepted_providers_utility[skill] = {}

    # --------------------GS ALGORITHM RELATED METHODS--------------------------
    def reset_for_GS(self):
        self.neighbors = []

    def update_neighbors_by_skill(self):
        self.neighbors_by_skill = {}
        for neighbor in self.neighbors:
            for skill in self.neighbors_skill[neighbor]:
                if skill not in self.neighbors_by_skill:
                    self.neighbors_by_skill[skill] = [neighbor]
                else:
                    self.neighbors_by_skill[skill].append(neighbor)

    def update_terminated(self):
        self.terminated = {}
        # skills that will play this round of GS
        for skill in self.neighbors_by_skill:
            self.terminated[skill] = False

    def initialize_GS_has_not_offered(self):
        self.GS_has_not_offered = {}
        for skill in self.neighbors_by_skill:
            self.GS_has_not_offered[skill] = [sp for sp in self.neighbors_by_skill[skill]
                                              if (sp in self.util_j[skill]
                                                  and self.util_j[skill][sp] >= self.utility_threshold_for_acceptance)]

    # initiates util_j dict
    def reset_util_j(self):
        self.util_j = {}
        for skill in self.neighbors_by_skill.keys():
            self.util_j[skill] = {}

    def reset_GS_has_offered(self):
        self.GS_has_offered = {}
        for skill in self.neighbors_by_skill:
            self.GS_has_offered[skill] = []

    # todo update this function to be more abstract - go to temp simulation entity
    def update_cap(self):
        for skill in self.sim_temp_temp_skills_needed:
            if self.sim_temp_max_required[skill] > self.sim_temp_temp_skills_needed[skill]:
                self.sim_temp_max_required[skill] = self.sim_temp_temp_skills_needed[skill]

            if skill in self.neighbors_by_skill and len(self.neighbors_by_skill[skill]) < self.sim_temp_max_required[skill]:
                self.sim_temp_max_required[skill] = len(self.neighbors_by_skill[skill])

    def update_time_per_skill_unit(self, time):
        for skill in self.sim_temp_temp_skills_needed:
           self.time_per_skill_unit[skill] = self.temp_simulation_entity.get_care_time(skill,time)


    def initialize(self):
        self.update_neighbors_by_skill()
        self.update_cap() #update cup to be the minimum between number of neighbors & max cup

        self.reset_GS_has_offered()
        self.GS_SP_choices = {}

        self.reset_util_j()

        self.update_terminated()

        self.calculate_utilities()
        self.send_utilities()

        self.initialize_GS_has_not_offered()
        self.make_and_send_GS_offers()

    # 2 - algorithm compute (single agent response to iteration)
    def compute(self):
        self.update_GS_needs()  # update temporary approvals

        self.make_and_send_GS_offers()

        self.GS_SP_choices = {}

    def update_GS_needs(self):
        for sp, choice in self.GS_SP_choices.items():
            choice_sr = choice[0]
            choice_skill = choice[1]
            if choice_sr == self.id_:
                self.GS_accepted_providers[choice_skill].add(sp)
                self.GS_accepted_providers_utility[choice_skill][sp] = self.util_j[choice_skill][sp]
            else:
                for skill in self.GS_accepted_providers:
                    if sp in self.GS_accepted_providers[skill]:
                        self.GS_accepted_providers[skill].remove(sp)
                        del self.GS_accepted_providers_utility[skill][sp]

        self.GS_has_not_offered = {}
        for skill in self.neighbors_by_skill:
            self.GS_has_not_offered[skill] = [sp for sp in self.neighbors_by_skill[skill]
                                              if (sp not in self.GS_has_offered[skill] and sp in self.util_j[skill]
                                                  and self.util_j[skill][sp] >= self.utility_threshold_for_acceptance)]

            if (len(self.GS_has_not_offered[skill]) == 0 or
                    (len(self.GS_accepted_providers[skill]) == self.sim_temp_max_required[skill])):
                self.terminated[skill] = True
            else:
                self.terminated[skill] = False

    def send_utilities(self):
        for neighbor in self.neighbors:
            neighbor_utils = {}
            for skill in self.util_j:
                if neighbor in self.util_j[skill]:
                    neighbor_utils[skill] = self.util_j[skill][neighbor]
            msg = BidMsg(self.id_, neighbor, copy.deepcopy(neighbor_utils))
            self.mailer.send_msg(msg)

    def send_offer_msgs(self, offers_by_neighbor):
        for neighbor in offers_by_neighbor:
            msg = BidMsg(self.id_, neighbor, offers_by_neighbor[neighbor])
            self.mailer.send_msg(msg)

    # 4 - receive incoming information from neighbors
    def agent_receive_a_single_msg(self, msg):
        if isinstance(msg, ServiceProposalMsg):
            self.offer_recive_by_skill.append(msg.information)
            for skill in self.skills_needed:
                if msg.information.travle_time+ self.mailer.current_time + self.time_per_skill_unit[skill] < self.max_time:
                    self.neighbors.append(msg.sender)
                    break

            if self.all_round_neighbor_skills[msg.sender]:
                all_round_neighbor_skills[msg.sender].append(msg.information.skill)
            else:
                all_round_neighbor_skills[msg.sender] = msg.information.skill

            if msg.sender in self.neighbors: #todo!!
                joint_skills = dict([skill for skill in msg.information["skills"].items() if skill[0] in self.sim_temp_temp_skills_needed
                                     and self.neighbor_arrival_times[msg.sender] + self.mailer.current_time +
                                     self.time_per_skill_unit[skill[0]] < self.max_time
                                     and len(self.GS_accepted_providers[skill[0]]) <
                                     self.sim_temp_max_required[skill[0]]])
                if joint_skills:
                    self.neighbors_skill[msg.sender] = joint_skills
                else:
                    self.neighbors.remove(msg.sender)

        elif isinstance(msg, BidMsg):
            self.GS_SP_choices[msg.sender] = msg.context

    def make_and_send_GS_offers(self):
        offers_by_neighbor = {}
        for skill in self.neighbors_by_skill:
            best_to_offer_skill = self.choose_best_SPs_to_offer(skill)
            for neighbor in best_to_offer_skill:
                if neighbor in offers_by_neighbor:
                    offers_by_neighbor[neighbor].append(skill)
                else:
                    offers_by_neighbor[neighbor] = [skill]

                self.GS_has_offered[skill].append(neighbor)

        self.send_offer_msgs(offers_by_neighbor)

    def choose_best_SPs_to_offer(self, skill):
        number_to_allocate = self.sim_temp_max_required[skill] - len(self.GS_accepted_providers[skill])

        utilities_for_options = copy.deepcopy(self.util_j[skill])
        to_remove = [sp for sp in utilities_for_options if sp not in self.GS_has_not_offered[skill]]
        for sp in to_remove:
            del utilities_for_options[sp]

        best_SPs_to_offer = []

        # self.print_options(utilities_for_options, skill)

        while number_to_allocate > 0 and len(utilities_for_options) > 0:
            # NCLO
            self.NCLO += Agent.number_of_comparisons(1, len(utilities_for_options))

            max_offer = max(utilities_for_options, key=utilities_for_options.get)
            best_SPs_to_offer.append(max_offer)
            # remove agent from the temp dict
            del utilities_for_options[max_offer]

            number_to_allocate = number_to_allocate - 1

        return best_SPs_to_offer

    def print_options(self, utilities_for_options, skill):
        utilities_for_options = sorted(utilities_for_options.items(), key=lambda item: item[1], reverse=True)
        print(self.id_, "for skill", skill, "choosing top", self.sim_temp_max_required[skill], "from:")
        for option in utilities_for_options:
            print("SP", option[0], "Util", option[1])

    def calculate_utilities(self):
        if bid_type == 0:
            update_simple_bids()
        if bid_type == 1:
            update_trancated_bids() #todo

    def update_simple_bids(self):
        """
        update self.util_j
        :return:
        """
        for skill in self.sim_temp_temp_skills_needed:
            for offer in self.offers_received_by_skill[skill]:
                #todo calca simple bid
               self.util_j[offer.skill] ={offer.provider: self.calc_simple_bid(offer)}


    def calc_simple_bid(self, offer):
        offer_receive_by_skills = copy.deepcopy(self.offers_received_by_skill)
        bid = 0
        only_the_sp_offer = {
            skill: [copy.deepcopy(o) for o in all_offers if o.provider == offer.provider and o.skill == offer.skill]
            for skill, all_offers in offer_receive_by_skills.items()}
        only_the_sp_offer = {k: v for k, v in only_the_sp_offer.items() if v}

        skills_needed_temp = {offer.skill: self.skills_needed[offer.skill]}

        only_sp_allocated_offers, _ = self.simulation_entity.allocated_offers(skills_needed_temp,
                                                                              only_the_sp_offer)
        utility_simple = self.simulation_entity.final_utility(only_sp_allocated_offers, cost=False)
        bid = utility_simple
        return round(max(0, bid), 2)

    def send_msgs(self):
        pass

    def update_utility_iterative(self): #todo!!! should be at simulation entity - the same as RPA
        pass
    def get_util(self, neighbors_working_together, skill):
        util = self.max_util[skill]
        total_skill = 0
        total_travel_times = 0
        for provider_id in neighbors_working_together:
            total_skill += self.neighbor_skills[provider_id][skill]
            total_travel_times += self.neighbor_arrival_times[provider_id]

        if total_skill > self.sim_temp_temp_skills_needed[skill]:
            total_skill = copy.deepcopy(self.sim_temp_temp_skills_needed[skill])

        # skill cover factor
        if total_skill / self.sim_temp_temp_skills_needed[skill] < 1:
            util *= total_skill / self.sim_temp_temp_skills_needed[skill]

        # penalty for delay * distance = utility lost for arrival
        util -= self.penalty_for_delay * total_travel_times

        # cap function
        util *= cap(len(neighbors_working_together), self.sim_temp_max_required[skill])

        return util

    # todo - this is the new one
    # def get_util(self, neighbors_working_together, skill):
    #     util = self.max_util[skill]
    #     total_skill = 0
    #
    #     for provider_id in neighbors_working_together:
    #         total_skill += self.neighbor_skills[provider_id][skill]
    #
    #     if total_skill > self.sim_temp_temp_skills_needed[skill]:
    #         total_skill = copy.deepcopy(self.sim_temp_temp_skills_needed[skill])
    #
    #     # skill cover factor
    #     if total_skill / self.sim_temp_temp_skills_needed[skill] < 1:
    #         util *= total_skill / self.sim_temp_temp_skills_needed[skill]
    #
    #     # cap function
    #     util *= cap(len(neighbors_working_together), self.sim_temp_max_required[skill])
    #
    #     return util

    def update_specific_utilities(self, neighbors_considered, skill, util):
        number_sharing = len(neighbors_considered) + len(self.GS_accepted_providers[skill])

        for neighbor in neighbors_considered:
            if neighbor not in self.util_j[skill]:
                self.util_j[skill][neighbor] = 0

            if self.util_j[skill][neighbor] < round(util / number_sharing, 2):
                self.util_j[skill][neighbor] = round(util / number_sharing, 2)
            else:
                util -= self.util_j[skill][neighbor]
                number_sharing -= 1

    # todo - this is the new one
    # def update_specific_utilities(self, neighbors_considered, skill, util):
    #     number_sharing = len(neighbors_considered) + len(self.GS_accepted_providers[skill])
    #
    #     for neighbor in self.GS_accepted_providers[skill]:
    #         if self.GS_accepted_providers_utility[skill][neighbor] >= round(util / number_sharing, 2):
    #             util -= self.GS_accepted_providers_utility[skill][neighbor]
    #             number_sharing -= 1
    #             continue
    #
    #     for neighbor in neighbors_considered:
    #         travel_time = self.neighbor_arrival_times[neighbor]
    #         util = round(util / number_sharing - travel_time * self.penalty_for_delay, 2)
    #
    #         if util <= 0:
    #             self.util_j[skill][neighbor] = 0
    #         else:
    #             self.util_j[skill][neighbor] = util

    def check_termination(self):
        for skill, termination in self.terminated.items():
            if not termination:
                return False
        return True

    # --------------------GS ALGORITHM POST-PROCESSING RELATED METHODS--------------------------
    def retrieve_GS_solution_events(self):

        new_services = self.retrieve_services()
        previous_services = self.current_services
        self.current_services = []

        current_time = self.mailer.current_time
        events = []
        # sp needs to leave
        for service in previous_services:
            if service not in new_services:
                if service.arrival_time < current_time:
                    leaving_event = ProviderLeaveRequesterEvent(arrival_time=current_time,
                                                                provider=service.provider, requester=self.id_,
                                                                skill=service.skill)
                    events.append(leaving_event)

            for skill in self.GS_accepted_providers:
                if service.provider in self.GS_accepted_providers[skill]:
                    break
            else:
                msg = GSUpdateServiceMessage(sender_id=self.id_, receiver_id=service.provider, context=None)
                self.mailer.send_msg(msg)

        for service in new_services:
            is_continuing_service = [s for s in previous_services if s == service]

            if is_continuing_service and is_continuing_service[0].arrival_time < current_time:
                provider_arrival_time = is_continuing_service[0].arrival_time
                provider_added_work_time = service.duration
                provider_leave_time = round(is_continuing_service[0].last_workload_use + provider_added_work_time, 2)
                provider_amount = int(round((provider_leave_time - provider_arrival_time)
                                            / self.time_per_skill_unit[service.skill], 2))
                service.amount = provider_amount
                service.arrival_time = provider_arrival_time
                service.leaving_time = provider_leave_time
                service.duration = round(service.leaving_time - service.arrival_time, 2)
                service.last_workload_use = is_continuing_service[0].last_workload_use

                leaving_event = ProviderLeaveRequesterEvent(arrival_time=service.leaving_time,
                                                            provider=service.provider, requester=self.id_,
                                                            skill=service.skill)
                events.append(leaving_event)

            else:
                arrival_event = ProviderArriveToRequesterEvent(arrival_time=service.arrival_time,
                                                               provider=service.provider, requester=self.id_,
                                                               skill=service.skill)
                events.append(arrival_event)

                leaving_event = ProviderLeaveRequesterEvent(arrival_time=service.leaving_time,
                                                            provider=service.provider, requester=self.id_,
                                                            skill=service.skill)
                events.append(leaving_event)

            msg = GSUpdateServiceMessage(sender_id=self.id_, receiver_id=service.provider, context=service)
            self.mailer.send_msg(msg)

            self.current_services.append(service)

        return events

    # def retrieve_services(self):
    #     temp_skills_needed_temp = copy.deepcopy(self.sim_temp_temp_skills_needed)
    #     all_services = []
    #
    #     for skill in self.GS_accepted_providers:
    #         service_skill_available_dict = {}
    #         services = []
    #         for sp in self.GS_accepted_providers[skill]:
    #
    #             if skill in self.working_by_skill and sp in self.working_by_skill[skill]:
    #                 already_serving = [s for s in self.current_services if s.provider == sp and s.skill == skill]
    #                 arrival_time = already_serving[0].last_workload_use
    #             else:
    #                 arrival_time = round(self.neighbor_arrival_times[sp] + self.mailer.current_time, 2)
    #
    #             service = DSRM_Variable_Assignment(sp, self.id_, skill, self.current_location,
    #                                                amount=1, duration=self.time_per_skill_unit[skill],
    #                                                arrival_time=arrival_time,
    #                                                leaving_time=round(arrival_time + self.time_per_skill_unit[skill],
    #                                                                   2),
    #                                                last_workload_use=arrival_time)
    #             services.append(service)
    #             if self.all_round_neighbor_skills[sp][skill] > 1:
    #                 service_skill_available_dict[service] = [self.all_round_neighbor_skills[sp][skill] - 1]
    #
    #             temp_skills_needed_temp[skill] -= 1
    #
    #         while temp_skills_needed_temp[skill] > 0 and service_skill_available_dict:
    #             import math
    #             even_load = math.floor(temp_skills_needed_temp[skill] / (len(service_skill_available_dict)))
    #             extra = None
    #
    #             if even_load == 0:
    #                 extra = temp_skills_needed_temp[skill]
    #
    #             to_remove = []
    #             for offer_stats, skill_left in service_skill_available_dict.items():
    #                 min_ability = min(skill_left[0], even_load)
    #                 if even_load == 0 and skill_left[0] > 0 and extra > 0:
    #                     min_ability = 1
    #                     extra -= 1
    #                 offer_stats.amount += min_ability
    #                 offer_stats.leaving_time += self.time_per_skill_unit[skill] * min_ability
    #                 offer_stats.leaving_time = round(offer_stats.leaving_time, 2)
    #                 offer_stats.duration += round(self.time_per_skill_unit[skill] * min_ability, 2)
    #                 skill_left[0] -= min_ability
    #                 temp_skills_needed_temp[skill] -= min_ability
    #
    #                 # no skill left
    #                 if skill_left[0] == 0:
    #                     to_remove.append(offer_stats)
    #
    #             for key in to_remove:
    #                 del service_skill_available_dict[key]
    #
    #         all_services.extend(services)
    #
    #     return all_services

    # todo - new version
    def retrieve_services(self):
        temp_skills_needed_temp = copy.deepcopy(self.sim_temp_temp_skills_needed)
        all_services = []

        for skill in self.GS_accepted_providers:
            service_skill_available_dict = {}
            services = []
            for sp in self.GS_accepted_providers[skill]:
                if skill in self.working_by_skill and sp in self.working_by_skill[skill]:
                    already_serving = [s for s in self.current_services if s.provider == sp and s.skill == skill]
                    arrival_time = already_serving[0].last_workload_use
                else:
                    arrival_time = round(self.neighbor_arrival_times[sp] + self.mailer.current_time, 2)
                service = DSRM_Variable_Assignment(sp, self.id_, skill, self.current_location,
                                                   amount=1, duration=self.time_per_skill_unit[skill],
                                                   arrival_time=arrival_time,
                                                   leaving_time=round(arrival_time + self.time_per_skill_unit[skill],
                                                                      2),
                                                   last_workload_use=arrival_time)
                services.append(service)
                if self.all_round_neighbor_skills[sp][skill] > 1:
                    service_skill_available_dict[service] = [self.all_round_neighbor_skills[sp][skill] - 1]

                self.skills_needed_temp[skill] -= 1

            while self.skills_needed_temp[skill] > 0 and service_skill_available_dict:
                # order offers by next skill unit work start
                service_skill_available_dict = dict(
                    sorted(service_skill_available_dict.items(), key=lambda service: service[0].leaving_time))
                offer_stats = next(iter(service_skill_available_dict.items()))

                # don't let stay overtime
                if offer_stats[0].leaving_time + round(self.time_per_skill_unit[skill], 2) > self.max_time:
                    del service_skill_available_dict[offer_stats[0]]
                    continue

                # arrival time
                offer_stats[0].leaving_time += self.time_per_skill_unit[skill]
                offer_stats[0].leaving_time = round(offer_stats[0].leaving_time, 2)
                # skill left
                offer_stats[0].amount += 1
                offer_stats[0].duration += round(self.time_per_skill_unit[skill], 2)
                offer_stats[1][0] -= 1
                self.skills_needed_temp[skill] -= 1

                # no skill left
                if offer_stats[1][0] == 0:
                    del service_skill_available_dict[offer_stats[0]]

            all_services.extend(services)

        return all_services

    # --------------------SIMULATION RELATED METHODS--------------------------
    def provider_arrives_to_requester(self, provider_id, skill, current_time):
        if skill not in self.amount_working:
            self.amount_working[skill] = 0

        if skill not in self.working_by_skill:
            self.working_by_skill[skill] = []

        self.working_by_skill[skill].append(provider_id)
        if current_time not in self.simulation_times_for_utility[skill]:
            self.simulation_times_for_utility[skill][current_time] = self.amount_working[skill]

        self.amount_working[skill] += 1

    def provider_leaves_requester(self, provider_id, skill, current_time):
        self.update_skills_received(current_time)

        self.current_services = [service for service in self.current_services
                                 if not (service.skill == skill and service.provider == provider_id)]

        self.working_by_skill[skill].remove(provider_id)

        if current_time not in self.simulation_times_for_utility[skill]:
            self.simulation_times_for_utility[skill][current_time] = self.amount_working[skill]

        self.amount_working[skill] -= 1

    def update_skills_received(self, current_time):
        for service in self.current_services:
            if service.arrival_time <= current_time and service.last_workload_use < current_time:  # provider has already arrived
                skills_received = int(round(current_time - service.last_workload_use, 2) /
                                      self.time_per_skill_unit[service.skill])

                self.sim_temp_skills_needed[service.skill] -= skills_received

                if self.sim_temp_skills_needed[service.skill] == 0:
                    del self.sim_temp_skills_needed[service.skill]

                service.last_workload_use += self.time_per_skill_unit[service.skill] * skills_received
                service.last_workload_use = round(service.last_workload_use, 2)
def find_ratio_of_travel_complete(time_travel_begin, arrival_time, current_time):
    return (current_time - time_travel_begin) / (arrival_time - time_travel_begin)