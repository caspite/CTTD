from Simulator.SimulationComponents import ServiceProvider,calc_distance


class Provider(ServiceProvider):
    def __init__(self, _id, skill_set, utility_threshold_for_acceptance=50, travel_speed=5,
                 location=[0.0, 0.0], time_born=0):
        ServiceProvider.__init__(self, _id=_id, time_born=time_born, location=location, skills=list(skill_set.keys())
                                 , speed=travel_speed)
        # Provider Variables
        self.skill_set = skill_set  # {skill: amount}
        self.init_skill_workload(skills_set=skill_set)

        self.utility_threshold_for_acceptance = utility_threshold_for_acceptance



