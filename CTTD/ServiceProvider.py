import enum
import copy
import abc

from CTTD.entity import Entity
from CTTD.problem_companents import *


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

    def __init__(self, _id, time_born, location, speed, skills=[], status =Status.IDLE,
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
        :rtype [skill]
        :param status: the service provider status in the simulation
        :rtype Status
        :param base_location: if has one
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
        self. workload =dict.fromkeys(skills,0) # initiate the workload of each skill to 0

    def update_workload_each_skill(self,skill, workload):
        """

        :param skill: The skill
        :param workload: The workload of the skill
        :rtype float
        :return: None
        """
        self.workload[skill] = workload if skill in self.workload.keys() else False

    def provide_service(self, skill, workload):
        """
        reduce the workload of a skill
        :param skill: the providable skill
        :param workload: the workload should by reduce
        :return: boolean if the workload is above the capacity
        """
        self.workload[skill] -= workload if skill in self.workload.keys() and self.workload[skill] >= workload\
            else False
