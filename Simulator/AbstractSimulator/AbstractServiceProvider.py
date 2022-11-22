from Simulator.SimulationComponents import ServiceProvider,calc_distance


class Provider(ServiceProvider):
    def __init__(self, _id, skill_set, utility_threshold_for_acceptance=50, travel_speed=5,
                 location=[0.0, 0.0], time_born=0):
        ServiceProvider.__init__(self, _id=_id, time_born=time_born, location=location, skills=skill_set.keys
                                 , speed=travel_speed)
        # Provider Variables
        self.skill_set = skill_set  # {skill: amount}
        self.work_time_i = {}  # {requester: work time per skill unit}
        self.init_skill_workload(skills_set=skill_set)

        self.utility_threshold_for_acceptance = utility_threshold_for_acceptance

    # 1 - calculate travel time by distance and speed
    def travel_time(self, start_location, end_location):
        distance = calc_distance(start_location, end_location)
        distance_in_time = round(distance / self.travel_speed, 2)
        return distance_in_time
