import math


class Entity:
    """
        Class that represents a basic entity in the simulation
    """

    def __init__(self, _id, last_time_updated=0, location=[0.0, 0.0]):
        """
        :param _id: the entity id
        :param last_time_updated: the last time that the entity updated (initial is time born)
        :param location:  the entity current location type: list of coordination
        """

        self._id = _id
        self.last_time_updated = last_time_updated
        self.location = location

    def update_location(self, location):
        """
        :param location: the next entity location
        :return: None
        """
        self.location = location

    def update_last_time(self, tnow):
        """
        :param tnow: next time update
        :return: None
        """
        self.last_time_updated = tnow if tnow > self.last_time_updated else Exception\
            ("times bug! last time in higher then tnow!")

    def distance_from_other_entity(self,other):
        """
        :param other: other entity
        :return: distance between self and other entity
        :rtype: float
        """
        return calc_distance(self.location, other.location) if type(other) == Entity else Exception("Not an entity!")

    def __str__(self):
        return 'id: ' + self._id + ' location: '.join(self.location) + ' last time update: ' + self.last_time_updated

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        return self._id == other._id


def calc_distance(location1, location2):
    """
    :param location1: entity 1 location list of coordination
    :param location2: entity 1 location list of coordination
    :return: Euclidean distance
    :rtype float
    """
    return math.dist(location1, location2)


def calc_distance_between_tow_entities(entity1: Entity, entity2: Entity):
    return calc_distance(entity1.location,entity2.location)
