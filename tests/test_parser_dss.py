from schg import OffLoad, OnLoad, State, FromDSS, SCHGError, SwitchingError


def test_all_switches() -> None:
    path = "tests/simple_dss/master.dss"
    sys = FromDSS(path)
    expected = {
        "virtual": OnLoad("virtual", State.ON),
        "671692": OffLoad("671692", State.ON),
        "virtual2": OnLoad("virtual2", State.OFF),
    }
    assert sys.switches == expected


def test_raise_error() -> None:
    path = "tests/simple_dss/master.dss"
    sys = FromDSS(path)
    try:
        sys.toggle_sw("671692")
        assert False
    except SCHGError as e:
        assert e.args[0] == [SwitchingError.OFFLOAD_SWITCHING_ON_LOAD]


def test_raise_error2() -> None:
    path = "tests/simple_dss/master.dss"
    sys = FromDSS(path)
    try:
        sys.toggle_sw("virtual2")
        assert False
    except SCHGError as e:
        assert e.args[0] == [
            SwitchingError.CAUSES_MESH,
            SwitchingError.CAUSES_SUBSTATIONS_INTERCONNECTION,
        ]


def test_13bus() -> None:
    path = "tests/13bus/IEEE13Nodeckt.dss"
    sys = FromDSS(path)
    expected = {
        "virtual": OnLoad("virtual", State.ON),
        "671692": OffLoad("671692", State.ON),
    }
    assert sys.switches == expected
