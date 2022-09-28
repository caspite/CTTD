

class Casualty:
    def __init__(self, init_RPM=12, t_born=0, id=0, disaster_site_id=0,):
        """
        :type init_RPM: int
        :type t_born: float
        :type id: int
        :type disaster_site_id: int

        """
        self.disaster_site_id = disaster_site_id
        self._id = id
        self._t_born = t_born
        self._init_RPM = init_RPM
        self.current_RPM = self._init_RPM
        self.activities = ('treatment', 'uploaded', 'transportation')
        self.scheduled_activities = {k: None for k in self.activities}  # activity: time (float)
        self.preformed_activities = {k: None for k in self.activities}  # activity: time (float)
        self.scheduled_status = 'waiting'
        self.preformed_status = 'waiting'

    # updated performances
    def receive_treatment(self, time):
        self.preformed_activities['treatment'] = time
        self.preformed_status = 'receive treatment'

    def uploaded(self, time):
        self.preformed_activities['uploaded'] = time
        self.preformed_status = 'uploaded'

    def evacuated(self, time):
        self.preformed_activities['transportation'] = time
        self.preformed_status = 'evacuated'

    # updated schedule
    def schedule_treatment(self, time):
        self.scheduled_activities['treatment'] = time
        self.scheduled_status = 'schedule treatment'

    def schedule_upload(self, time):
        self.scheduled_activities['uploaded'] = time
        self.scheduled_status = 'schedule upload'

    def schedule_transportation(self, time):
        self.scheduled_activities['transportation'] = time
        self.scheduled_status = 'schedule transportation'

    # return the survival by a given time and the activities performance
    def get_survival_by_time_and_performance(self, time=None):
        if time is None: time = self.t_born
        # todo add rmp calc

    # return the survival by a given time and the activities scheduled
    def get_survival_by_time_and_schedule(self, time=None):
        if time is None: time = self.t_born
        # todo add rpm calc

    def __eq__(self, other):
        return self._id == other._id

    def __str__(self):
        return 'Id: '+self._id + ' RPM: '+self._init_RPM + ' schedule status: ' + self.scheduled_status \
               + 'preformed status: ' + self.preformed_status
