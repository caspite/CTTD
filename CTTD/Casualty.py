import RPM


class Casualty:
    def __init__(self, init_RPM=12, triage='NON_URGENT', t_born=0, _id=0, disaster_site_id=0,):
        """
        :type init_RPM: int
        :type t_born: float
        :type _id: int
        :type disaster_site_id: int

        """
        self.disaster_site_id = disaster_site_id
        self._id = _id
        self._t_born = t_born
        self._init_RPM = RPM(init_RPM, triage)
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
        # todo update current rpm

    def uploaded(self, time):
        self.preformed_activities['uploaded'] = time
        self.preformed_status = 'uploaded'
        # todo update current rpm

    def evacuated(self, time):
        self.preformed_activities['transportation'] = time
        self.preformed_status = 'evacuated'
        # todo update current rpm

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
        self._init_RPM.get_survival_by_time_deterioration()

    # return the survival by a given time and the activities scheduled
    def get_survival_by_time_and_schedule(self, time=None):
        if time is None: time = self.t_born
        temp_rpm, temp_time = self.rmp_and_time_by_schedule(time)
        RPM(temp_rpm).get_survival_by_time_deterioration(temp_time)
        # todo add rpm calc

    def rmp_and_time_by_schedule(self, time):
        # todo - finish this func
        match self.preformed_status:
            case 'waiting':
                match self.scheduled_status:
                    case 'waiting':
                        return self._init_RPM, time
                    case 'schedule treatment':
                        pass
                    case 'uploaded':
                        pass
            case 'receive treatment':
                match self.scheduled_status:
                    case 'waiting':
                        return self._init_RPM, time
                    case 'schedule treatment':
                        pass
                    case 'uploaded':
                        pass

            case 'uploaded':
                match self.scheduled_status:
                    case 'waiting':
                        return self._init_RPM, time
                    case 'schedule treatment':
                        pass
                    case 'uploaded':
                        pass
            case 'evacuated':
                return self.current_RPM, self.preformed_activities['transportation']

    def __eq__(self, other):
        return self._id == other._id

    def __str__(self):
        return 'Id: '+self._id + ' RPM: '+self._init_RPM + ' schedule status: ' + self.scheduled_status \
               + 'preformed status: ' + self.preformed_status
