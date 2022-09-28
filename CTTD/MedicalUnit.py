from abstract_service_orientd_simulation.ServiceEntities import *
import enum


class MedicalUnit(ServiceProvider):
    """
    Class that represent a medical unit. medical unit can provide one of the skills:
    treatment, upload, transportation for urgent, medium, and non-urgent casualties
    """

    def __init__(self, _id, time_born, location, speed, skills, unit_type, max_capacity):
        """
        initial medical unit
        :param _id: The entity id
        :param time_born: the time that the entity was born
        :param location: the entity location
        :param speed: the medical unit speed drive
        :param skills: list of skill that the medical unit can provide.
        if skill in None - the list of the skill will be field by the medical unit type
        :rtype (cttdSkill) tuple
        :param unit_type: the medical unit type (ALS, BLS, Motorcycle)
        :rtype MedicalUnitType
        :param max_capacity: maximum score of capacity each skill has score #todo????
        :rtype int

        """
        ServiceProvider.__init__(_id, time_born, location, speed, skills)
        self.max_capacity = max_capacity
        self.unit_type = unit_type
        self.is_full = False  # is_full: is the medical unit full
        self.uploaded_casualties = []  # the casualties that currently on to the medical unit
        self.load_capacity()

    def load_capacity(self):
        """
        After arriving to a hospital the medical unit is refilled
        the capacity is determined by MedicalUnitType object

        """
        self.max_capacity = self.unit_type.get_maximum_capacity()
        map(lambda s: self.update_workload_each_skill(s, self.unit_type.get_max_capacity_by_skill(s)), self.skills)

    def load_casualty(self,casualty):
        """
        Add casualty to loaded casualties
        :param casualty:
        :return: none
        """
        self.uploaded_casualties.append(casualty)

    def arrived_to_hospital(self, hospital: Entity): # todo - move this to a
        """
        when medical unit arrives to a hospital it initiates the loaded casualties and refill
        :return:
        """
        self.load_capacity()
        self.uploaded_casualties.clear()
        self.update_location(hospital.location)

    def update_status(self, status: Status):
        self.status = status

    def update_time(self, time: float):
        self.update_last_time(time)


class MedicalUnitTypeName(enum):
        BLS = 0
        ALS = 1
        Motorcycle = 2


class MedicalUnitType:
    """
    object that hold the medical unit type and the params that derived from the medical unit type
    """

    def __init__(self, medical_unit_type_name):
        """

        :param medical_unit_type_name:
        :rtype MedicalUnitTypeName
        :param max_capacity
        :rtype int
        :param skills
        :type [skill]
        :param max_workload_for_skill
        :type dict{skill:float}
        """
        self.medical_unit_type_name = medical_unit_type_name
        self.max_capacity = self.get_max_capacity()
        self.skills = self.get_skills()
        self.max_workload_for_skill = self.get_max_workload_for_all_skills () # dict of skill: number of workload
        self.speed = self.get_speed()

    def get_max_capacity(self):
        pass

    def get_skills(self):
        pass

    def get_max_workload_for_all_skills(self):
        pass

    def get_speed(self):
        pass

    def get_maximum_capacity(self):
        pass




