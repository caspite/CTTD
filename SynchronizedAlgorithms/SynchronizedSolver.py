import copy
import math

from Solver.SOMAOP.BasicSOMAOP import SP, SR

dbug = True


class VariableAssignment:
    def __init__(self, provider, requester, skill, location, amount=None, duration=None, arrival_time=None, leaving_time=None,
                 utility=None):
        self.provider = provider
        self.requester = requester
        self.skill = skill
        self.location = location
        self.amount = amount
        self.duration = duration
        self.arrival_time = arrival_time
        self.leaving_time = leaving_time
        self.utility = utility

    def __str__(self):
        return "SP " + str(self.provider) + " SR " + str(self.requester) + " skill " + str(self.skill) + \
               " arrival: " + str(self.arrival_time) + " leaving: " + str(self.leaving_time) \
               + " amount: " + str(self.amount) + "utility:" + str(self.utility)

    # for comparing with ==
    def __eq__(self, other):
        return self.provider == other.provider and self.requester == other.requester and self.skill == other.skill

    # for inserting in hashable objects like list
    def __hash__(self):
        return self.requester

    # for copy.deepcopy()
    def __deepcopy__(self, memodict={}):
        copy_object = VariableAssignment(self.provider, self.requester, self.skill, self.location, self.amount, self.duration,
                                         self.arrival_time, self.leaving_time, self.utility)
        return copy_object


class SynchronizedSolverSOMAOP(object):
    def __init__(self, problem_id, providers: [SP], requesters: [SR], mailer, termination):
        # solver variables
        self.problem_id = problem_id
        self.all_providers = providers
        self.all_requesters = requesters
        self.mailer = mailer  # the mailer - deliver message only
        self.termination = termination
        self.agents = providers + requesters

        # NCLO variables
        self.NCLO = 0
        self.total_util_over_NCLO = {0: 0}

        # initialized
        self.assign_neighbors()

    # 3 - creates neighboring agents by threshold distance - symmetrical
    def assign_neighbors(self):
        for provider in self.all_providers:
            for requester in self.all_requesters:
                if requester.provider_require(provider=provider):
                    skills_in_common = [s for s in provider.skill_set if s in requester.skills_needed]
                    provider.neighbors.append(requester.getId())
                    requester.neighbors.append(provider.getId())
                    provider_skills_available_in_common = {}
                    requester_skills_needs_in_common = {}
                    for skill in skills_in_common:
                        requester.neighbors_by_skill[skill].append(provider.getId())
                        provider_skills_available_in_common[skill] = provider.skill_set[skill]
                        requester_skills_needs_in_common[skill] = requester.skills_needed[skill]
                        provider.xi_size += 1
                        domain_opt = VariableAssignment(provider.getId(), requester.getId(), skill,
                                                        copy.deepcopy(requester.location))
                        provider.domain.append(domain_opt)
                    provider.neighbor_locations[requester.getId()] = copy.deepcopy(requester.location)

    def meat_mailer(self, mailer):
        self.mailer = mailer

    # initialize the agents if necessary and start run algorithm
    def execute(self):
        for agent in self.all_providers + self.all_requesters:
            agent.initielized(self)
        self.execute_algorithm()

    def execute_algorithm(self):
        raise NotImplementedError()

    # finds agent by id (from providers and requesters)
    def get_agent_by_id(self, agent_id):
        for agent in self.all_providers + self.all_requesters:
            if agent.getId() == agent_id:
                return agent
        else:
            return None

    def reset_agent_NCLOS(self):
        for agent in self.all_providers+self.all_requesters:
            agent.NCLO = 0

    def find_max_NCLO(self):
        max_NCLO = 0
        for agent in self.all_providers+self.all_requesters:
            if agent.NCLO > max_NCLO:
                max_NCLO = agent.NCLO
        return max_NCLO

    def update_current_NCLO(self):
        self.NCLO += self.find_max_NCLO()

    def record_data(self):
        util = self.calculate_global_utility()
        self.update_current_NCLO()
        self.reset_agent_NCLOS()
        self.total_util_over_NCLO[self.NCLO] = util
        if dbug: print('NCLO: %s, Utility: %s'% (self.NCLO, util))

    def calculate_global_utility(self):
        raise NotImplementedError()
