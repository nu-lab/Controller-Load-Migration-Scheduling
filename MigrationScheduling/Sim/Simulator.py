"""The Simulator class is used to simulate load migration scheduling
instances. It serves as the base class to simulators using specific
distributions.

"""
import random
import numpy as np
from abc import ABC, abstractmethod
from MigrationScheduling.Data import Migration



class Simulator(ABC):
    """Used to simulate a loda migration scheduling instance.

    Attributes
    ----------
    _migrations: list
        A list of `Migration` objects specifying the simulated migrations.
    _num_migrations: int
        An integer representing the number of migrations.
    _controllers: list
        A list of three element tuples specifying the simulated controllers.
        The first element is an integer representing the number of migrations
        with this controller as destination, the second is a float
        representing the maximum load incurred for a migration to this
        controller and the third is a float representing the sum of load
        incurred for a migration to this controller.
    _num_controllers: int
        An integer representing the number of controllers.
    _qos_groups: list
        A list of integers representing the number of migrations belonging
        to each QoS group.
    _num_qos_groups: int
        An integer representing the number of QoS groups.

    """
    def __init__(self):
        self._migrations = []
        self._num_migrations = 0
        self._controllers = []
        self._num_controllers = 0
        self._qos_groups = []
        self._num_qos_groups = 0

    def run(self, num_migrations, output_file):
        """Simulates and outputs a load migration scheduling instance.

        Parameters
        ----------
        num_migrations: int
            The number of migrations in the simulated instance.
        output_file: str
            A string representing the name of the file to which the instance
            will be output.

        Returns
        -------
        None

        """
        self._num_migrations = num_migrations
        self._initialize(num_migrations)
        self._migrations = [self._create_migration(migration_idx)
                            for migration_idx in range(self._num_migrations)]
        self._output_simulated_instance(output_file)

    def _initialize(self, num_migrations):
        """Initializes the simulator.

        The number of controllers and number of qos_groups are selected and
        their parameters are initialized for the simulation.

        Parameters
        ----------
        num_migrations: int
            An integer representing the number of migrations in the
            simulation.

        Returns
        -------
        None

        """
        self._num_controllers = max(
            2, int(np.random.normal(0.3, 0.1) * num_migrations))
        self._controllers = [[0, 0.0, 0.0]
                             for _ in range(self._num_controllers)]

        self._num_qos_groups = max(
            0, int(np.random.normal(0.7, 0.1) * num_migrations))
        self._qos_groups = [0 for _ in range(self._num_qos_groups)]

    def _assign_migration_to_qos_groups(self, migration):
        """Simulates the assignment of `migration` to QoS groups.

        The simulator samples a random number x of QoS groups to which the
        migration will be assigned and then the x groups are chosen the set
        of all groups uniformly at random.

        Parameters
        ----------
        migration: Migration
            The `Migration` object being assigned to QoS groups.

        Returns
        -------
        set
            A set of strings representing the QoS groups to which the
            migration was assigned.

        """
        groups = set()
        num_groups = min(self._num_qos_groups, max(0,
            int(np.random.normal(0.3, 0.4) * self._num_qos_groups)))
        group_ids = random.sample(range(self._num_qos_groups), num_groups)
        for group_id in group_ids:
            groups.add("g{}".format(group_id))
            self._qos_groups[group_id] += 1
        return groups

    def _add_load_to_controller(self, controller_idx, load):
        """Adds `load` to the controller identified by `controller_idx`.

        `load` represents the load of a migration being added to the
        controller identified by `controller_idx`. The number of migrations
        belonging to the controller is incremented by 1 and the maximum load
        and sum of loads for migrations belonging to the controller are
        updated based on `load`.

        Parameters
        ----------
        controller_idx: int
            An integer denoting the controller to which the load is being
            added.
        load: float
            A float representing the load being added to the controller.

        Returns
        -------
        None

        """
        self._controllers[controller_idx][0] += 1
        self._controllers[controller_idx][1] = max(
            load, self._controllers[controller_idx][1])
        self._controllers[controller_idx][2] += load


    def _assign_to_controllers(self, load):
        """Picks controllers for a migration with load of `load`.

        A source and destination controller is chosen uniformly at random
        from the set of controllers.

        Parameters
        ----------
        load: float
            A float representing the load of a migration being assigned to a
            controller.

        Returns
        -------
        int, int
            Two integer representing the index of the controller serving as
            the source and destination controllers for the migration,
            respectively.

        """
        src, dst = random.sample(range(self._num_controllers), 2)
        self._add_load_to_controller(src, load)
        self._add_load_to_controller(dst, load)
        return src, dst

    def _construct_migration_from_load(self, migration_idx, load):
        """Constructs a migration from `load` based on `migration_idx`.

        A source and destination controller is chosen for the migration and
        a `Migration` object is constructed for `migration_idx`.

        Parameters
        ----------
        migration_idx: int
            An integer representing the index of the migration.
        load: float
            A float representing the load incurred for the migration.

        Returns
        -------
        Migration
            A `Migration` object representing the migration for
            `migration_idx`.

        """
        src, dst = self._assign_to_controllers(load)
        return Migration("s{}".format(migration_idx),
                         "c{}".format(src), "c{}".format(dst), load)

    def _create_migration(self, migration_idx):
        """Simulates a new migration.

        For the simulated migration a random controller is picked as the
        destination controller and a random load is chosen for the migration.

        Parameters
        ----------
        migration_idx: int
            An integer representing the index of the migration being
            simulated.

        Returns
        -------
        Migration
            A `Migration` object representing a simulated migration.

        """
        migration = self._setup_migration(migration_idx)
        for group in self._assign_migration_to_qos_groups(migration):
            migration.add_qos_group(group)
        return migration

    def _get_controller_cap_bounds(self, controller_idx):
        """Gets capacity bounds for controller `controller_idx`.

        The lower bound on the capacity is the maximum load of a migration
        destined to the controller and the upper bound is the sum of the
        loads of the migrations destined to the controller.

        Parameters
        ----------
        controller_idx: int
            An integer representing the index for the controller.

        Returns
        -------
        float, float
            Two floats representing the lower bound and upper bound on the
            controller capacity, respectively.

        """
        lb = self._controllers[controller_idx][1]
        ub = self._controllers[controller_idx][2]
        return lb, ub

    def _get_migration_line(self, migration):
        """Construct the migration line for `migration` for the output file.

        The migration line for `migration` consists of the name of the
        switch and the name of the destination controller for the migration.
        This is followed by the load incurred on the controller during the
        migration and the set of QoS groups. All arguments are space
        separated.

        Parameters
        ----------
        migration: Migration
            A `Migration` object representing the migration for which the
            migration line is generated.

        Returns
        -------
        str
            A string representing the migration line.

        """
        return "{0} {1} {2} {3} {4}\n".format(
            migration.get_switch(), migration.get_src_controller(),
            migration.get_dst_controller(), migration.get_load(),
            " ".join(migration.get_groups()))

    def _output_simulated_instance(self, output_file):
        """Outputs the simulated load migration scheduling instance.

        The simulated load migration scheduling instance is written to
        `output_file`.

        Parameters
        ----------
        output_file: str
            A string representing the name of the file to which the instance
            will be written.

        Returns
        -------
        None

        """
        with open(output_file, "w") as migration_file:
            for migration in self._migrations:
                migration_file.write(self._get_migration_line(migration))
            for controller_idx in range(self._num_controllers):
                if self._controllers[controller_idx][0] > 0:
                    migration_file.write(
                        self._get_controller_line(controller_idx))
            for qos_idx in range(self._num_qos_groups):
                if self._qos_groups[qos_idx] > 0:
                    migration_file.write(self._get_qos_line(qos_idx))

    @abstractmethod
    def _setup_migration(self, migration_idx):
        """Sets up a migration for `migration_idx`.

        The setup involves simulating a load for the migration and choosing
        a random source and destination controller.

        Parameters
        ----------
        migration_idx: int
            An integer representing the index of the migration being set up.

        Returns
        -------
        Migration
            The created `Migration` object.

        """
        pass

    @abstractmethod
    def _get_controller_line(self, controller_idx):
        """Constructs the controller line for `controller_idx`.

        The controller line for `controller_idx` consists of the name of
        the controller and its capacity. This capacity is the amount of load
        the controller can accommodate from migrations in a single round. All
        arguments are space separated.

        Parameters
        ----------
        controller_idx: int
            An integer representing the index of the controller for which
            the line is generated.

        Returns
        -------
        str
            A string representing the controller line.

        """
        pass

    @abstractmethod
    def _get_qos_line(self, qos_idx):
        """Constructs the QoS line for `qos_idx`.

        The QoS line for `qos_idx` consists of the name of the QoS group and
        its capacity. This capacity is the maximum amount of migrations
        within this group that can be completed in a single round. All
        arguments are space separated.

        Parameters
        ----------
        qos_idx: int
            An integer representing the index of the QoS group for which the
            line is generated.

        Returns
        -------
        str
            A string representing the QoS line.

        """
        pass
