"""Simulates load migration scheduling instances having a random number
of migrations chosen uniformly at random within the supplied bounds. The
simulation is done using the `WeightedGaussianSimulator` class.

"""
import sys
import random
from MigrationScheduling import analysis, specs, utils
from MigrationScheduling.Sim import WeightedGaussianSimulator

utils.initialize_seeds(specs.SEED_NUM)

if __name__ == "__main__":
    output_path = sys.argv[1]
    num_instances = int(sys.argv[2])
    lb = max(specs.MIN_MIGRATIONS, int(sys.argv[3]))
    ub = max(lb, int(sys.argv[4]))
    low_prop = float(sys.argv[5])
    med_prop = float(sys.argv[6])

    sim_args = {'low_prop': low_prop, 'med_prop': med_prop}

    instance_sizes = random.choices(range(lb, ub + 1), k=num_instances)
    analysis.create_simulated_instances(
        WeightedGaussianSimulator, sim_args,
        instance_sizes, specs.SMALL_IDX, output_path)
