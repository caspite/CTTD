from Simulator.SimulationComponents import ServiceRequester


class DisasterSite(ServiceRequester):

    def __init__(self, _id, location, time_born, skills, services, time_max, casualties=[]):
        ServiceRequester.__init__(_id, time_born, location, skills, services, time_max)
        self.casualties = casualties

    def add_casualties(self, casualties):
        self.casualties.append(casualties)


