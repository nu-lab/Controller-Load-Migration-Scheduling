import os
import gurobipy as gp
from gurobipy import GRB
from MigrationScheduling import algorithms
from MigrationScheduling.Model import Optimizer

DIR = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_PATH = os.path.join(DIR, os.path.join("instances", "migrations1.txt"))

# indices of network objects
SWITCH_IDS = [0, 1, 2, 3, 4]
ROUND_IDS = [0, 1, 2, 3, 4]
CONTROLLER_IDS = [0, 1]
GROUP_IDS = [0, 1, 2]

# switch loads
LOADS = {0: 13.24, 1: 8.83, 2: 17.9, 3: 7.65, 4: 7.68}

# controller capacities
CONTROLLER_CAPS = {0: 39.31, 1: 17.90}

# group capacities
GROUP_CAPS = {0: 1, 1: 1, 2: 1}

# switches migrating from each source controller
SRC_CONTROLLERS = {0: {0, 1, 2, 3, 4}, 1: set()}

# switches migrating to each destination controller
DST_CONTROLLERS = {0: set(), 1: {0, 1, 2, 3, 4}}

# group membership
GROUPS = {0: {3}, 1: {0}, 2: {0, 2}}

def test_optimizer_without_resiliency():
    # direct modelling
    m = gp.Model('test-migration')
    x_vars = m.addVars(SWITCH_IDS, ROUND_IDS, vtype=GRB.BINARY, name="x")
    lambda_var = m.addVar(name="lambda")
    m.setObjective(lambda_var, GRB.MINIMIZE)
    m.addConstrs((x_vars.sum(i, '*') == 1 for i in SWITCH_IDS), 'migrate')
    m.addConstrs((r * x_vars[i, r] <= lambda_var
                  for i in SWITCH_IDS for r in ROUND_IDS), "bounds")
    m.addConstrs((sum(LOADS[i] * x_vars[i, r] for i in DST_CONTROLLERS[j])
                  <= CONTROLLER_CAPS[j]
                  for j in CONTROLLER_IDS for r in ROUND_IDS
                  if len(DST_CONTROLLERS[j]) > 0),
                  "controller_cap")
    m.addConstrs((sum(x_vars[i, r] for i in GROUPS[l]) <= GROUP_CAPS[l]
                  for l in GROUP_IDS for r in ROUND_IDS),
                  "group_cap")
    m.optimize()

    # optimizer
    optimizer = Optimizer()
    optimizer.get_model_data(DATA_PATH)
    optVal = optimizer.build_ip_model(resiliency=False, verbose=False)
    assert round(optVal, 2) == round(m.objVal, 2)


def test_optimizer_with_resiliency():
    # direct modelling
    m = gp.Model('test-migration')
    x_vars = m.addVars(SWITCH_IDS, ROUND_IDS, vtype=GRB.BINARY, name="x")
    lambda_var = m.addVar(name="lambda")
    m.setObjective(lambda_var, GRB.MINIMIZE)
    m.addConstrs((x_vars.sum(i, '*') == 1 for i in SWITCH_IDS), 'migrate')
    m.addConstrs((r * x_vars[i, r] <= lambda_var
                  for i in SWITCH_IDS for r in ROUND_IDS), "bounds")
    m.addConstrs((sum(LOADS[i] * x_vars[i, r]
                  for i in SRC_CONTROLLERS[j].union(DST_CONTROLLERS[j]))
                  <= CONTROLLER_CAPS[j]
                  for j in CONTROLLER_IDS for r in ROUND_IDS
                  if (len(SRC_CONTROLLERS[j]) > 0 or
                      len(DST_CONTROLLERS[j]) > 0)),
                  "controller_cap")
    m.addConstrs((sum(x_vars[i, r] for i in GROUPS[l]) <= GROUP_CAPS[l]
                  for l in GROUP_IDS for r in ROUND_IDS),
                  "group_cap")
    m.optimize()

    # optimizer
    optimizer = Optimizer()
    optimizer.get_model_data(DATA_PATH)
    optVal = optimizer.build_ip_model(resiliency=True, verbose=False)
    assert round(optVal, 2) == round(m.objVal, 2)


def test_vff_heuristic_no_resilience():
    optimizer = Optimizer()
    optimizer.get_model_data(DATA_PATH)
    vff_val = algorithms.vector_first_fit(optimizer.instance_data(), False)

    # vff solution value is 4:
    # - migration 0 is scheduled in round 1
    # - migrations 1 and 3 are scheduled in round 2
    # - migration 2 is scheduled in round 3
    # - migration 4 is scheduled in round 4
    assert vff_val == 4

def test_vff_heuristic_with_resilience():
    optimizer = Optimizer()
    optimizer.get_model_data(DATA_PATH)
    vff_val = algorithms.vector_first_fit(optimizer.instance_data(), True)

    # vff solution value is 4:
    # - migration 0 is scheduled in round 1
    # - migrations 1 and 3 are scheduled in round 2
    # - migration 2 is scheduled in round 3
    # - migration 4 is scheduled in round 4
    assert vff_val == 4
