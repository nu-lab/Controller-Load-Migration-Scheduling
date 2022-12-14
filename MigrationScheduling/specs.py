"""A set of specifications and global parameters used throughout the load
migration scheduling project.

"""

# minimum number of migrations in a simulated instance
MIN_MIGRATIONS = 1

# index for new small instances
SMALL_IDX = 0

# index for new large instances
LARGE_IDX = 0

# cutoff for deciding whether an instance is small or large. The cutoff is
# in terms of number of migrations. Small instances can be solved directly
# with the optimizer, large instances require heuristic methods.
SMALL_CUTOFF = 250

# number of choices used in the current bottleneck first algorithm when
# selecting the number of candidate migrations from the bottleneck
# constraint.
CBF_CHOICES = 2

# seed number used when setting seeds for reproducibility of experiments
SEED_NUM = 42

# a map representing the colors to use for plotting.
COLOR_MAP = {"VFF": "blue", "CBF": "orange", "OPT": "black"}

# a map representing the styles to use for plotting
STYLE_MAP = {"VFF": "-", "CBF": "^", "OPT": '-.'}

# a map representing the linewidths for plotting
LINEWIDTH_MAP = {"VFF": 2, "CBF": 1, "OPT": 1}

# alpha values for plotting
ALPHA_MAP = {"VFF": 1.0, "CBF": 0.6, "OPT": 1.0}

# the set of valid bottlenek settings
BOTTLENECK_SETTINGS = {'low', 'medium', 'high'}
