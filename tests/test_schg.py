from schg import LinkError, OnLoad, OffLoad, SCHGError, State, SwitchingError, System
from uuid import uuid1


def test_two_switches_with_same_name_returns_same_hash() -> None:
    name = str(uuid1())
    sw0 = OnLoad(name, State.ON, on_substation=True)
    sw1 = OffLoad(str(name), State.ON)

    assert sw0.__hash__() == sw1.__hash__()


def test_two_switches_with_same_name_are_equal() -> None:
    name = str(uuid1())
    sw0 = OnLoad(name, State.ON, on_substation=True)
    sw1 = OffLoad(name, State.ON)

    assert sw0 == sw1


def test_onload_toggle_no_system() -> None:
    sw0 = OnLoad(str(uuid1()), State.ON)

    try:
        sw0.toggle_state()
        assert False
    except SCHGError as e:
        assert e.args[0] == [SwitchingError.SYSTEM_NOT_DEFINED]


def test_offload_toggle_no_system() -> None:
    sw0 = OffLoad(str(uuid1()), State.ON)

    try:
        sw0.toggle_state()
        assert False
    except SCHGError as e:
        assert e.args[0] == [SwitchingError.SYSTEM_NOT_DEFINED]


def test_two_switches_common_link() -> None:
    sw0 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sw1 = OffLoad(str(uuid1()), State.ON)
    sys = System()
    sys.link(sw0, sw1)


def test_two_switches_equal_link() -> None:
    name = str(uuid1())
    sw0 = OnLoad(name, State.ON, on_substation=True)
    sw1 = OnLoad(name, State.OFF)
    sys = System()

    try:
        sys.link(sw0, sw1)
        assert False
    except SCHGError as exception:
        assert exception.args[0] == [LinkError.SELF_LINKING]


def test_two_switches_equal_different_type() -> None:
    name = str(uuid1())
    sw0 = OnLoad(name, State.ON)
    sw1 = OffLoad(name, State.OFF)
    sys = System()

    try:
        sys.link(sw0, sw1)
        assert False
    except SCHGError as exception:
        assert exception.args[0] == [LinkError.SELF_LINKING]


def test_two_switches_substations_different_state_1() -> None:
    sw0 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sw1 = OnLoad(str(uuid1()), State.OFF, on_substation=True)
    sys = System()
    sys.link(sw0, sw1)


def test_two_switches_substations_different_state_2() -> None:
    sw0 = OnLoad(str(uuid1()), State.OFF, on_substation=True)
    sw1 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sys = System()
    sys.link(sw0, sw1)


def test_two_switches_substations_same_state_ON() -> None:
    sw0 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sw1 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sys = System()

    try:
        sys.link(sw0, sw1)
        assert False, "This must error"
    except SCHGError as exception:
        assert exception.args[0] == [LinkError.SUBSTATION_LINKING]


def test_two_switches_substations_same_state_OFF() -> None:
    sw0 = OnLoad(str(uuid1()), State.OFF, on_substation=True)
    sw1 = OnLoad(str(uuid1()), State.OFF, on_substation=True)
    sys = System()
    sys.link(sw0, sw1)


def test_two_switches_toggle_first_not_meshed() -> None:
    sw0 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sw1 = OnLoad(str(uuid1()), State.ON)
    sys = System()
    sys.link(sw0, sw1)

    sw0.toggle_state()

    assert not sys.ismeshed


def test_two_switches_toggle_second_not_meshed() -> None:
    sw0 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sw1 = OnLoad(str(uuid1()), State.ON)
    sys = System()
    sys.link(sw0, sw1)

    sw0.toggle_state()

    assert not sys.ismeshed


def test_two_switches_substations_connected() -> None:
    sw0 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sw1 = OnLoad(str(uuid1()), State.OFF, on_substation=True)
    sys = System()

    sys.link(sw0, sw1)

    try:
        sw1.toggle_state()
        assert False
    except SCHGError as e:
        assert e.args[0] == [SwitchingError.CAUSES_SUBSTATIONS_INTERCONNECTION]


def test_three_switches_not_meshed() -> None:
    sw0 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sw1 = OffLoad(str(uuid1()), State.ON)
    sw2 = OnLoad(str(uuid1()), State.OFF)
    sys = System()

    sys.link(sw0, sw1)
    sys.link(sw1, sw2)

    sw2.toggle_state()

    assert not sys.ismeshed


def test_three_switches_toggle_mesh() -> None:
    sw0 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sw1 = OffLoad(str(uuid1()), State.ON)
    sw2 = OnLoad(str(uuid1()), State.OFF)
    sys = System()

    sys.link(sw0, sw1)
    sys.link(sw1, sw2)
    sys.link(sw2, sw0)
    try:
        sw2.toggle_state()
        assert False
    except SCHGError as e:
        assert e.args[0] == [SwitchingError.CAUSES_MESH]


def test_three_switches_not_substations_connected() -> None:
    sw0 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sw1 = OffLoad(str(uuid1()), State.ON)
    sw2 = OnLoad(str(uuid1()), State.OFF)
    sys = System()

    sys.link(sw0, sw1)
    sys.link(sw1, sw2)

    sw2.toggle_state()

    assert not sys.is_substations_connected


def test_three_switches_substations_connected() -> None:
    sw0 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sw1 = OffLoad(str(uuid1()), State.ON)
    sw2 = OnLoad(str(uuid1()), State.OFF, on_substation=True)
    sys = System()

    sys.link(sw0, sw1)
    sys.link(sw1, sw2)

    try:
        sw2.toggle_state()
        assert False
    except SCHGError as e:
        assert e.args[0] == [SwitchingError.CAUSES_SUBSTATIONS_INTERCONNECTION]


def test_two_switches_toggle_state_to_off_offload_on_load() -> None:
    sw0 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sw1 = OffLoad(str(uuid1()), State.ON)
    sys = System()
    sys.link(sw0, sw1)

    try:
        sw1.toggle_state()
        assert False
    except SCHGError as e:
        assert e.args[0] == [SwitchingError.OFFLOAD_SWITCHING_ON_LOAD]


def test_two_switches_toggle_state_to_on_offload_on_load() -> None:
    sw0 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sw1 = OffLoad(str(uuid1()), State.OFF)
    sys = System()
    sys.link(sw0, sw1)

    try:
        sw1.toggle_state()
        assert False
    except SCHGError as e:
        assert e.args[0] == [SwitchingError.OFFLOAD_SWITCHING_ON_LOAD]


def test_three_switches_toggle_state_to_off_offload_on_load_and_sub_connection() -> (
    None
):
    sw0 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sw1 = OffLoad(str(uuid1()), State.OFF)
    sw2 = OnLoad(str(uuid1()), State.ON, on_substation=True)
    sys = System()

    sys.link(sw0, sw1)
    sys.link(sw1, sw2)

    try:
        sw1.toggle_state()
        assert False
    except SCHGError as e:
        assert e.args[0] == [
            SwitchingError.CAUSES_SUBSTATIONS_INTERCONNECTION,
            SwitchingError.OFFLOAD_SWITCHING_ON_LOAD,
        ]
