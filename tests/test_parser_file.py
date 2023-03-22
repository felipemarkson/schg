from schg import OffLoad, OnLoad, State, FromFile, SCHGError, SwitchingError


def test_all_switches() -> None:
    path = "tests/simple_file/master.schg"
    sys = FromFile(path)
    expected = {
        "sw1": OnLoad("sw1", State.ON),
        "sw2": OffLoad("sw2", State.ON),
        "sw3": OnLoad("sw3", State.OFF),
    }
    assert sys.switches == expected


def test_raise_error() -> None:
    path = "tests/simple_file/master.schg"
    sys = FromFile(path)
    try:
        sys.toggle_sw("sw2")
        assert False
    except SCHGError as e:
        assert e.args[0] == [SwitchingError.OFFLOAD_SWITCHING_ON_LOAD]


def test_raise_error2() -> None:
    path = "tests/simple_file/master.schg"
    sys = FromFile(path)
    try:
        sys.toggle_sw("sw3")
        assert False
    except SCHGError as e:
        assert e.args[0] == [
            SwitchingError.CAUSES_MESH,
            SwitchingError.CAUSES_SUBSTATIONS_INTERCONNECTION,
        ]
