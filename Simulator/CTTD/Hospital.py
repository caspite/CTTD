from Simulator.SimulationComponents import Entity


class Hospital(Entity):
    def __init__(self, _id, location, t_born, max_capacity):
        Entity.__init__(location=location, last_time_updated=t_born, _id=_id)
        self.current_capacity = max_capacity
        self.max_capacity = max_capacity
        self.casualties  # list of the casualties in the hospital

    def add_casualties(self, casualties: list):
        self.current_capacity -= casualties.size()
        self.casualties.append(casualties)
