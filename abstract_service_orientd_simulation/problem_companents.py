import random

_width = None
_length = None


# the map for the problem
class MapSimple:
    """
    The class represents a map for the simulation. The entities must be located by the def generate_location.
    One map for each simulation.
    """

    def __init__(self, length, width, seed):
        """
        :param length: The length of the map
        :param width: The length of the map
        :param seed: seed for random object
        """
        self.length = length
        self.width = width
        global _length
        _length = length
        global _width
        _width = width
        self.rand = random.Random(seed)

    def generate_location(self):
        """
        :return: random location on map
        :type: list of floats
        """
        x1 = self.rand.random()
        x2 = self.rand.random()
        return [self.width*x1, self.length*x2]

    def get_the_center_of_the_map_location(self):
        return [self.width / 2, self.length / 2]


# the skills of the problem
class Skill:
    """
    Class that represent all the skills that entity can have or require
    """
    def __init__(self, skill_name=None, skill_id=0):
        """

        :param skill_name:  The skill type name (if dkill name is none, name = skill id as str)
        :rtype str
        :param skill_id: the skill id
        :rtype int
        """
        self.skill_id = skill_id
        self.skill_name = skill_name if skill_name==None else self.skill_name = str(self.skill_id)

    def __eq__(self, other):
        return self.skill_id == other.skill_id

    def __str__(self):
        return self.skill_name


