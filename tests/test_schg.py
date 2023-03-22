from schg import LinkError, OnLoad, OffLoad, SCHGError, State, SwitchingError, System


def test_two_switches_with_same_name_returns_same_hash() -> None:
    sw0 = OnLoad("sw1", State.ON, on_substation=True)
    sw1 = OffLoad("sw1", State.ON)

    assert sw0.__hash__() == sw1.__hash__()


def test_two_switches_with_same_name_are_equal() -> None:
    sw0 = OnLoad("sw1", State.ON, on_substation=True)
    sw1 = OffLoad("sw1", State.ON)

    assert sw0 == sw1


def test_onload_toggle_no_system() -> None:
    sw0 = OnLoad("sw1", State.ON)

    try:
        sw0.togle_state()
        assert False
    except SCHGError as e:
        assert e.args[0] == [SwitchingError.SYSTEM_NOT_DEFINED]


def test_offload_toggle_no_system() -> None:
    sw0 = OffLoad("sw1", State.ON)

    try:
        sw0.togle_state()
        assert False
    except SCHGError as e:
        assert e.args[0] == [SwitchingError.SYSTEM_NOT_DEFINED]


def test_two_switches_common_link() -> None:
    sw0 = OnLoad("sub", State.ON, on_substation=True)
    sw1 = OffLoad("sw1", State.ON)
    sys = System()
    sys.link(sw0, sw1)


def test_two_switches_equal_link() -> None:
    sw0 = OnLoad("sw1", State.ON, on_substation=True)
    sw1 = OnLoad("sw1", State.OFF)
    sys = System()

    try:
        sys.link(sw0, sw1)
        assert False
    except SCHGError as exception:
        assert exception.args[0] == [LinkError.SELF_LINKING]


def test_two_switches_equal_different_type() -> None:
    sw0 = OnLoad("sw1", State.ON)
    sw1 = OffLoad("sw1", State.OFF)
    sys = System()

    try:
        sys.link(sw0, sw1)
        assert False
    except SCHGError as exception:
        assert exception.args[0] == [LinkError.SELF_LINKING]


def test_two_switches_substations_different_state_1() -> None:
    sw0 = OnLoad("sw1", State.ON, on_substation=True)
    sw1 = OnLoad("sw2", State.OFF, on_substation=True)
    sys = System()
    sys.link(sw0, sw1)


def test_two_switches_substations_different_state_2() -> None:
    sw0 = OnLoad("sw1", State.OFF, on_substation=True)
    sw1 = OnLoad("sw2", State.ON, on_substation=True)
    sys = System()
    sys.link(sw0, sw1)


def test_two_switches_substations_same_state_ON() -> None:
    sw0 = OnLoad("sw1", State.ON, on_substation=True)
    sw1 = OnLoad("sw2", State.ON, on_substation=True)
    sys = System()

    try:
        sys.link(sw0, sw1)
        assert False, "This must error"
    except SCHGError as exception:
        assert exception.args[0] == [LinkError.SUBSTATION_LINKING]


def test_two_switches_substations_same_state_OFF() -> None:
    sw0 = OnLoad("sw1", State.OFF, on_substation=True)
    sw1 = OnLoad("sw2", State.OFF, on_substation=True)
    sys = System()
    sys.link(sw0, sw1)


def test_two_switches_toggle_first_not_meshed() -> None:
    sw0 = OnLoad("sub", State.ON, on_substation=True)
    sw1 = OnLoad("sw1", State.ON)
    sys = System()
    sys.link(sw0, sw1)

    sw0.togle_state()

    assert not sys.ismeshed


def test_two_switches_toggle_second_not_meshed() -> None:
    sw0 = OnLoad("sub", State.ON, on_substation=True)
    sw1 = OnLoad("sw1", State.ON)
    sys = System()
    sys.link(sw0, sw1)

    sw0.togle_state()

    assert not sys.ismeshed


def test_three_switches_not_meshed() -> None:
    sw0 = OnLoad("sw0", State.ON, on_substation=True)
    sw1 = OffLoad("sw1", State.ON)
    sw2 = OnLoad("sw2", State.OFF)
    sys = System()

    sys.link(sw0, sw1)
    sys.link(sw1, sw2)

    sw2.togle_state()

    assert not sys.ismeshed


def test_three_switches_togle_mesh() -> None:
    sw0 = OnLoad("sw0", State.ON, on_substation=True)
    sw1 = OffLoad("sw1", State.ON)
    sw2 = OnLoad("sw2", State.OFF)
    sys = System()

    sys.link(sw0, sw1)
    sys.link(sw1, sw2)
    sys.link(sw2, sw0)
    try:
        sw2.togle_state()
        assert False
    except SCHGError as e:
        assert e.args[0] == [SwitchingError.CAUSES_MESH]


def test_three_switches_not_substations_connected() -> None:
    sw0 = OnLoad("sw0", State.ON, on_substation=True)
    sw1 = OffLoad("sw1", State.ON)
    sw2 = OnLoad("sw2", State.OFF)
    sys = System()

    sys.link(sw0, sw1)
    sys.link(sw1, sw2)

    sw2.togle_state()

    assert not sys.is_substations_connected


def test_three_switches_substations_connected() -> None:
    sw0 = OnLoad("sw0_", State.ON, on_substation=True)
    sw1 = OffLoad("sw1_", State.ON)
    sw2 = OnLoad("sw2_", State.OFF, on_substation=True)
    sys = System()

    sys.link(sw0, sw1)
    sys.link(sw1, sw2)

    try:
        sw2.togle_state()
        assert False
    except SCHGError as e:
        assert e.args[0] == [SwitchingError.CAUSES_SUBSTATIONS_INTERCONNECTION]


# def test_two_switches_toggle_state_same_state() -> None:
#     sw0 = OnLoad("sub", State.ON, on_substation=True)
#     sw1 = OffLoad("sw1", State.ON)
#     link(sw0, sw1)

#     assert sw1.togle_state() == Err(SwitchError.ONLOAD_NOT_POSSIBLE)


# def test_two_switches_toggle_state_state_different() -> None:
#     sw0 = OnLoad("sw0", State.ON, on_substation=True)
#     sw1 = OffLoad("sw1", State.OFF)
#     link(sw0, sw1)

#     assert sw1.togle_state() == Err(SwitchError.ONLOAD_NOT_POSSIBLE)


# def test_two_switches_toggle_state_island_frist() -> None:
#     sw0 = OffLoad("sw0", State.ON)
#     sw1 = OffLoad("sw1", State.ON)
#     link(sw0, sw1)

#     assert sw0.togle_state() == Ok()


# def test_two_switches_toggle_state_island_second() -> None:
#     sw0 = OffLoad("sw0", State.ON)
#     sw1 = OffLoad("sw1", State.ON)
#     link(sw0, sw1)

#     assert sw1.togle_state() == Ok()


# def test_three_switches_err_on_togle_offload() -> None:
#     sw0 = OnLoad("sw0", State.ON, on_substation=True)
#     sw1 = OffLoad("sw1", State.ON)
#     sw2 = OnLoad("sw2", State.OFF)
#     assert link(sw0, sw1) == Ok()
#     assert link(sw1, sw2) == Ok()
#     assert link(sw2, sw0) == Ok()

#     assert sw1.togle_state() == Err(SwitchError.ONLOAD_NOT_POSSIBLE)


# def test_three_switches_err_on_togle_mesh() -> None:
#     sw0 = OnLoad("sw0", State.ON, on_substation=True)
#     sw1 = OffLoad("sw1", State.ON)
#     sw2 = OnLoad("sw2", State.OFF)
#     assert link(sw0, sw1) == Ok()
#     assert link(sw1, sw2) == Ok()
#     assert link(sw2, sw0) == Ok()

#     assert sw2.togle_state() == Err(SwitchError.CAUSES_MESH)


# def test_three_switches_err_on_togle_mesh_by_substation() -> None:
#     sw0 = OnLoad("sw0", State.ON, on_substation=True)
#     sw1 = OffLoad("sw1", State.ON)
#     sw2 = OnLoad("sw2", State.OFF, on_substation=True)
#     assert link(sw0, sw1) == Ok()
#     assert link(sw1, sw2) == Ok()

#     assert sw2.togle_state() == Err(SwitchError.CAUSES_MESH)
