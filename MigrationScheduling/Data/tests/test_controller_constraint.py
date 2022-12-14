import pytest
from unittest.mock import patch, MagicMock
from MigrationScheduling.Data import ControllerConstraint
from MigrationScheduling import exceptions as exc


VAL_STR = "MigrationScheduling.validation.validate_name"


@pytest.fixture(scope="function")
def control_const():
    with patch(VAL_STR, side_effect=None) as mock_val:
        control_const = ControllerConstraint('c2', 12.5)
    mock_val.assert_called_once_with('c2', 'c', 'Controller')
    return control_const


def test_instantiation(control_const):
    assert control_const.get_controller() == 'c2'
    assert control_const.get_controller_idx() == 2
    assert control_const.get_cap() == 12.5
    assert control_const.get_in_switches() == set()
    assert control_const.get_out_switches() == set()

@patch(VAL_STR, side_effect=exc.InvalidName(""))
def test_invalid_name(mock_validate):
    with pytest.raises(exc.InvalidName):
        ControllerConstraint("c7.5", 5)

def test_adding_switches(control_const):
    control_const.add_in_switch("s0")
    control_const.add_in_switch("s3")
    control_const.add_out_switch("s7")
    assert control_const.get_in_switches() == {"s0", "s3"}
    assert control_const.get_out_switches() == {"s7"}


def test_constraint_switches(control_const):
    control_const._in_switches = {"s0", "s3"}
    control_const._out_switches = {"s7"}
    assert control_const.get_constraint_switches(False) == {"s0", "s3"}
    assert control_const.get_constraint_switches(True) == {"s0", "s3", "s7"}

def test_str_no_switches(control_const):
    assert control_const.__str__() == ("Constraint for controller c2 " +
                                       "with a capacity of 12.50.\n")

def test_str_with_in_switches(control_const):
    control_const._in_switches = {"s0", "s3"}
    first_part = "Constraint for controller c2 with a capacity of 12.50.\n"
    second_part_1 = "Destination for switches: s0 s3\n"
    second_part_2 = "Destination for switches: s3 s0\n"
    assert control_const.__str__() in [first_part + second_part_1,
                                       first_part + second_part_2]

def test_str_with_out_switches(control_const):
    control_const._out_switches = {"s7"}
    const_str = ("Constraint for controller c2 with a capacity of 12.50.\n" +
                 "Source for switches: s7\n")
    assert control_const.__str__() == const_str
