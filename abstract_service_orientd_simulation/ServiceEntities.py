import enum
import functools
import math

from abstract_service_orientd_simulation.entity import Entity
from abstract_service_orientd_simulation.problem_companents import Skill


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
        self.workload = dict.fromkeys(skills, 0)  # initiate the workload of each skill to 0
        self.scheduled_services = [Service]
        # the services that were scheduled list of Service object

    def update_workload_each_skill(self, skill, capacity):
        """

        :param skill: The skill
        :param capacity: The workload of the skill
        :rtype float
        :return: None
        """
        self.workload[skill] = capacity if skill in self.workload.keys() else False

    def provide_service(self, skill, workload):
        """
        reduce the workload of a skill
        :param skill: the providable skill
        :param workload: the workload should be reduced from current capacity
        :return: boolean if the workload is above the capacity
        """
        self.workload[skill] -= workload if skill in self.workload.keys() and self.workload[skill] >= workload\
            else False

    def __str__(self):
        return " Service Provider id: " + self._id + " last update time: " + self.last_time_updated + \
               " current location: " + self.location + " free workload: " + self.workload

    def __eq__(self, other):
        self._id == other._id

    def get_free_workload(self, skill):
        """
        return the free workload for allocation by skill
        :return: float
        """
        return self.workload[skill]

    def reset_workload(self, skill, workload):
        self.workload[skill] = workload


class ServiceRequester(Entity):
    """
        A class that represent a service provider
    """

    def __init__(self, _id, time_born, location, skills, max_time=math.inf):
        """
        :param _id: the entity id
        :rtype int
        :param time_born: the entity born time (update as last time)
        :rtype float
        :param location: the current location of the entity - generated from map class
        :rtype [float]
        :param skills: list of require skills
        :rtype [skill]
        :param max_time: the maximum time fo each skill need to complete (infinity if not initiate)
        :rtype float

        """
        Entity.__init__(_id, time_born, location)
        self.max_time = max_time
        self.skills = skills
        self.skills_requirements = dict.fromkeys(skills, [0, 0, 1, max_time])
        # initiate the requirements of each skill. dict-> Skill: workload=0
        self.skills_definitions = dict.fromkeys(skills, [0, 1, max_time])
        # initiate the definitions of each skill. dict-> Skill: [max utility=0,cap=1,max time=max_time]

        self.finished = False  # when all the skill requirements completed true
        self.cap = 1  # the benefit from working simultaneously on few services
        self.scheduled_services = [Service]
        # the services that were scheduled list of Service object

    def reduce_skill_requirement(self, skill, workload):
        """
        Reduce the workload from a service by a skill
        :param skill: the reduced service id
        :type Skill
        :param workload: the workload to reduce
        :return: None if success else exception
        """
        self.skills_requirements[skill] -= workload if self.requirements[skill] > workload else \
            Exception("The workload is higher than the requirements")

    def add_scheduled_service(self, service):
        """
        add a service to schedule services
        :param service: the service provide
        """
        self.scheduled_services.append(service)

    def initiate_scheduled_services(self):
        """
        initiate all the scheduled services
        """
        self.scheduled_services.clear()

    def calc_utility_by_schedule(self):
        """
        calc the utility from scheduled services - this is used in extend class
        :return: the utility from scheduled services
        """
        raise Exception("This is an abstract method!")

    def allocate_requirements_by_providable_skills_time_workload(self, skill, workload, start_time):
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
    """
    a class that represent a service: composed of a skill and the workload to be provided in an SR

    """
    def __init__(self, _id, sr, skill, start_time, workload=1):
        """
        :param _id: the service id = service_requester_id + order id
        :rtype int
        :param sr: the service provider id
        :rtype: int
        :param skill: skills needed to complete the service
        :rtype Skill
        :param start_time: the time to start the service
        :rtype float
        :param workload: the amount of workload to be provided
        :rtype float

        """

        self.workload = workload
        self.start_time = start_time
        self.skill = skill
        self._id = _id
        self.sr = sr
        self.duration = self.calc_duration()
        self.utility = self.calc_utility()
        self.finished = False  # if the service completed

    def calc_utility(self):
        """
        :return: the utility from working on the service by start time, workload, number of service
        providers
        """
        return self.skill.calc_utility(self.workload, self.start_time)
