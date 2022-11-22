from abc import ABC

from Simulator.SimulationComponents import ServiceRequester


class Requester(ServiceRequester):
    def __init__(self, _id, time_born, skills_needed, location=[0.0, 0.0], utility_type=0, penalty_for_delay=0.95,
                 max_required={}, time_per_skill_unit={}, max_util=1000, max_time=10,
                 utility_threshold_for_acceptance=50, rate_util_fall=5):
        ServiceRequester.__init__(self, _id=_id, time_born=time_born, location=location,
                                  skills=skills_needed.keys, max_time=max_time)

        self.time_per_skill_unit = time_per_skill_unit  # {skill: time per unit} duration for skill unit
        self.utility_threshold_for_acceptance = utility_threshold_for_acceptance
        self.init_skill_definition(skills_needed=skills_needed, max_required=max_required, max_util=max_util)

        # utility variables
        self.penalty_for_delay = penalty_for_delay  # penalty multiplied by provider travel times
        self.rate_util_fall = rate_util_fall  # how much utility is affected by time

        self.simulation_times_for_utility = {}  # {time: amount working before}
        self.reset_simulation_times_for_utility()  # from maya's simulator - for the finite calculation

        self.util_j = {}  # {skill:{provider:utility}} from maya's simulator

    # 1 - calculates final utility according to team_simulation_times_for_utility dict
    def calc_utility_by_schedule(self, simulation_times=None):
        """

        :param simulation_times: {Skill:{time: amount working before}}
        :return: utility for times
        """
        if simulation_times is None:
            simulation_times = self.simulation_times_for_utility

        all_util = 0
        for skill, amount_needed in self.skills_requirements.items():
            if skill in simulation_times.keys():
                rate_of_util_fall = ((- self.max_util[skill] / self.rate_util_fall) / self.max_time)
                util_available = self.max_util[skill]
                util_received = 0
                last_time = 0
                total_amount_complete = 0
                for time, amount_working in simulation_times[skill].items():
                    time_elapsed = time - last_time
                    skills_complete = min(amount_needed - total_amount_complete,
                                          time_elapsed / self.time_per_skill_unit[skill])

                    if amount_working == 0:  # no service given in this time frame - util is lost
                        util_available += rate_of_util_fall * time_elapsed
                    else:  # service is given in this time frame - util is not lost
                        total_amount_complete += skills_complete
                        cap_multiplier = cap(amount_working, self.max_required[skill])
                        util = util_available * (skills_complete / amount_needed) * cap_multiplier
                        util_received += util
                        if total_amount_complete >= amount_needed:
                            break
                    last_time = time

                    if time > self.max_time:
                        break

                all_util += util_received
            # print("req",self.id_, "skill ", skill, "utility ", util_received)

        if all_util < 0:
            return 0

        return round(all_util, 2)

    def allocate_requirements_by_providable_skills_time_workload(self, skill, workload, start_time):
        """
        get a providable skills, start time and workload and scheduled them
        :return: update the self schedule raise exception - this is used in extend class
        """
        pass  # todo - delete?

    # initiates team_simulation_times_for_utility dict
    def reset_simulation_times_for_utility(self):
        for skill in self.skills:
            self.simulation_times_for_utility[skill] = {}


# 2 - cap function, defining the efficiency of a team at the SR
def cap(team, max_required):
    # linear
    if team == 0:
        return 0

    if team >= max_required:
        return 1

    rate = 0.5/(max_required - 1)
    cap_outcome = 0.5 + rate * (team - 1)

    return cap_outcome