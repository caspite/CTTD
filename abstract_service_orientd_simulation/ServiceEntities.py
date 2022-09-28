import enum
import functools
import math

from abstract_service_orientd_simulation.entity import Entity


class Status(enum.Enum):
    """
    Enum that represents the status of the player in the simulation
    """
    IDLE = 0
    ON_MISSION = 1
    TO_MISSION = 2


class ServiceProvider(Entity):
    """
    A class that represent a service provider
    """

    def __init__(self, _id, time_born, location, speed, skills, status=Status.IDLE,
                 base_location=None, productivity=1):
        """
        :param _id: the entity id
        :rtype int
        :param time_born: the entity born time (update as last time)
        :rtype float
        :param location: the current location of the entity - generated from map class
        :rtype [float]
        :param speed: the service provider speed
        :rtype float
        :param skills: list of providable skills
        :rtype (skill)
        :param status: the service provider status in the simulation
        :rtype Status
        :param base_location: The service provider base location case has one
        :rtype [float]
        :param productivity: entity productivity between 0 and 1
        :rtype float
        """
        Entity.__init__(_id, time_born, location)
        self.productivity = productivity
        self.base_location = base_location
        self.status = status
        self.skills = skills
        self.speed = speed
        self.capacity = dict.fromkeys(skills, 0)  # initiate the capacity of each skill to 0

    def update_workload_each_skill(self, skill, capacity):
        """

        :param skill: The skill
        :param capacity: The workload of the skill
        :rtype float
        :return: None
        """
        self.capacity[skill] = capacity if skill in self.capacity.keys() else False

    def provide_service(self, skill, workload):
        """
        reduce the workload of a skill
        :param skill: the providable skill
        :param workload: the workload should be reduced from current capacity
        :return: boolean if the workload is above the capacity
        """
        self.capacity[skill] -= workload if skill in self.capacity.keys() and self.capacity[skill] >= workload\
            else False

    def __str__(self):
        pass

    def __eq__(self, other):
        pass

    def get_free_capacity(self):
        pass

    def reset_capacity(self):
        pass


class ServiceRequester(Entity):
    """
        A class that represent a service provider
    """

    def __init__(self, _id, time_born, location, skills, services, time_max=math.inf):
        """
        :param _id: the entity id
        :rtype int
        :param time_born: the entity born time (update as last time)
        :rtype float
        :param location: the current location of the entity - generated from map class
        :rtype [float]
        :param skills: list of require skills
        :rtype [skill]
        :param time_max: the maximum time that the requirements need to complete (infinity if not initiate)
        :rtype float

        """
        Entity.__init__(_id, time_born, location)
        self.services = services  # the services needed to be completed. if all completed - finished
        self.time_max = time_max
        self.skills = skills
        self.requirements = dict.fromkeys(services, 0)  # initiate the requirements of each service to 0
        self.finished = False  # when all the requirements completed true
        self.cap = 1  # the benefit from working simultaneously on few services
        self.scheduled_services = dict.fromkeys(services, [0, self.last_time_updated, 0])
        # initiate the scheduled services of each skill to 0 workload and in the current time utility to 0

    def reduce_service_requirement(self, service, workload):
        """
        Reduce the workload from a service by a skill
        :param service: the reduced service id
        :type int
        :param workload: the workload to reduce
        :return: None if success else exception
        """
        self.requirements[service] -= workload if self.requirements[service] > workload else \
            Exception("The workload is higher than the requirements")

    def add_schedule_service(self, service, workload, start_time, number_service_providers):
        """
        schedule a service skill workload and time
        :param number_service_providers: the number of service providers working simultaneity
        :param service: the service provide
        :param workload: the amount of workload
        :param start_time: the start time
        :return:
        """
        self.scheduled_services[service] += [workload, start_time, service.calc_utility(workload, start_time,
                                                                                        number_service_providers)]  # add to scheduled services a service

    def initiate_scheduled_services(self):
        """
        initiate all the scheduled services
        :return:
        """
        for i in self.scheduled_services.keys():
            self.scheduled_services[i] = [0, self.last_time_updated, 0]

    def calc_utility_by_schedule(self):
        """
        calc the utility from schedule
        :return: the utility from scheduled services
        """
        # sum all utility from scheduled dict
        return functools.reduce(lambda a, b: a+b, self.scheduled_services.values()[2])

    def schedule_services_by_providable_skills_time_workload(self, skill, workload, start_time):
        """
        get a providable skills, start time and workload and scheduled them
        :return: update the self schedule raise exception - this is used in extend class
        """
        raise Exception('This is an abstract method!')

    def __str__(self):
        return " Service Require id: " + self._id + " last update time: " + self.last_time_updated +\
                " current utility: " + self.calc_utility_by_schedule()

    def __eq__(self, other):
        return self._id == other._id


class Service:
    def __init__(self, _id, skill, minimum_time, pre_service=None, workload=1, max_cap=1, max_utility=0):
        """

        :param _id: the service id = service_requester_id + order id
        :rtype int
        :param skill: skills needed to complete the service
        :rtype Skill
        :param minimum_time: the minimal time to start the service
        :rtype float
        :param pre_service: the id of the pre-service - not necessary
        :rtype int
        :param workload: the number of units of each skill
        :rtype {skill: float}
        :param max_cap: the maximum number of service providers needed to complete the service
        :param max_utility: the maximum utility can be derived from complete the service
        """
        self.max_utility = max_utility
        self.max_cap = max_cap
        self.workload = workload
        self.pre_service = pre_service
        self.minimum_time = minimum_time
        self.skill = skill
        self._id = _id

    def calc_utility(self, workload, start_time, number_service_providers):
        """
        :param number_service_providers:
        :param workload:
        :param start_time:
        :return: the utility from working on the service by start time, workload, number of service
        providers
        """
        pass
