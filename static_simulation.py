import pandas as pd
from Simulator.AbstractSimulator.AbstractSimulatorComponents import AbstractSimulatorCreator
from Simulator.CTTD.CttdSimulatorComponents import CttdSimulatorComponents
from Solver.SolverAbstract import Mailer, Agent
from SynchronizedAlgorithms.RPA.Main_RPA import RPA

dbug = True
SR_amount = [1]
SP_amount = [2]
problems_amount = 1
algorithm_type = [1, 2]  # 1 - RPA/DSA, 2 - DSRM / none
solver_type = [1, 2]  # 1-SOMAOP 2-DCOP
simulation_type = [1, 2]  # 1 - abstract, 2 - cttd
algorithm_version = [1]
bid_type = [1, 2]  # 1 - regular bid, 2 - shapley
termination = 250 # termination for RPA

# for DCOP privacy coherency
assignmentPrivacy = [0.0, 0.25, 0.5, 0.75, 1]
constraintPrivacy = [0.0, 0.25, 0.5, 0.75, 1]


# create simulation problems
def create_problems_simulation():
    ans = []
    for i in range(0, problems_amount):
        problem = create_new_problem(i)
        ans.append(problem)
    return ans


def create_new_problem(problem_id):
    if simulation == 1:
        new_prob = AbstractSimulatorCreator(number_of_providers=SP, number_of_requesters=SR, prob_id=problem_id)
    elif simulation == 2:
        new_prob = CttdSimulatorComponents(number_of_providers=SP, number_of_requesters=SR, prob_id=problem_id)
    return new_prob


# create solver for each problem and solve
def solve_problems(in_problems):
    for problem in in_problems:
        solver = create_synchronized_solver(problem)
        create_and_meet_mailer(solver.agents,problem.problem_id, solver)
        solver.execute_algorithm()


def create_synchronized_solver(problem):
    if p_type == 1:
        if algorithm == 1:
            return RPA(problem_id=problem.problem_id, providers=problem.providers, requesters=problem.requesters,
                      max_iteration=termination, bid_type=bid,algorithm_version=version)


def create_and_meet_mailer(agents: [Agent], problem_id, solver):
    mailer = Mailer(problem_id=problem_id, agents=agents)
    for a in agents: a.meet_mailer(mailer)
    solver.meat_mailer(mailer)
    return mailer

# export data to excel
def to_excel():
    string_name = "Simulator_%s_%s_problems_%s_SPs_%s_SRs"%(simulation, problems, SP, SR)
    writer = pd.ExcelWriter(string_name + '.xlsx', engine='openpyxl')
    writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)

    runInformation.to_excel(writer, sheet_name='Run Information')

    update_global_util_for_all_NCLOs()
    globalUtilityOverNCLODF = pandas.DataFrame.from_dict(data=globalUtilityOverNCLO)
    globalNCLOsDF = pandas.DataFrame(data=sorted(globalNCLOs), columns=['NCLO'])
    globalNCLOsDF.to_excel(writer, sheet_name='New Global Utility Over NCLO', startcol=0, index=False)
    globalUtilityOverNCLODF.to_excel(writer, sheet_name='New Global Utility Over NCLO', startcol=1, index=False)

    writer.save()

# main run simulation
if __name__ == '__main__':
    for simulation in simulation_type:
        for SR in SR_amount:
            for SP in SP_amount:
                if SP > SR:
                    for p_type in solver_type:
                        runInformation = initiateRunInformationDF()
                        for algorithm in algorithm_type:
                            for version in algorithm_version:
                                for bid in bid_type:
                                    if dbug:
                                        print("Running simulation. \n %s SPs, %s SRs problem type: "
                                              "%s \n algorithm %s version %s bid type: %s"
                                              % (SP, SR, p_type, algorithm, version, bid))
                                    problems = create_problems_simulation()
                                    solve_problems(in_problems=problems)
                                    to_excel()