__version__ = "0.1.0"

from abc import abstractmethod, ABC
from enum import Enum, auto
from typing import Iterable, List, Set, Tuple


class LinkError(Enum):
    SELF_LINKING = auto()
    SUBSTATION_LINKING = auto()


class SwitchError(Enum):
    ONLOAD_NOT_POSSIBLE = auto()
    CAUSES_MESH = auto()


class State(Enum):
    ON = 1
    OFF = 0


class Switch(ABC):
    @property
    @abstractmethod
    def on_substation(self) -> bool:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def state(self) -> State:
        ...

    @property
    def ison(self) -> bool:
        return bool(self.state.value)

    @abstractmethod
    def togle_state(self) -> None:
        ...

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Switch):
            return self.name == __o.name
        return False

    def __hash__(self) -> int:
        return hash(self.name)


_SetSw = Set["Switch"]


class OnLoad(Switch):
    def __init__(
        self,
        name: str,
        initial_state: State,
        *,
        on_substation: bool = False,
    ) -> None:
        self._name = name
        self.__state = initial_state
        self._on_substation = on_substation

    @property
    def on_substation(self) -> bool:
        return self._on_substation

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> State:
        return self.__state

    def togle_state(self) -> None:
        self.__state = State(not self.__state.value)


class OffLoad(Switch):
    def __init__(
        self,
        name: str,
        initial_state: State,
    ) -> None:
        self.__name = name
        self.__state = initial_state

    @property
    def on_substation(self) -> bool:
        return False

    @property
    def name(self) -> str:
        return self.__name

    @property
    def state(self) -> State:
        return self.__state

    def togle_state(self) -> None:
        self.__state = State(not self.__state.value)


class _Link:
    def __init__(self, sw1: Switch, sw2: Switch) -> None:
        if sw1 == sw2:
            raise ValueError(LinkError.SELF_LINKING)

        if sw1.on_substation and sw2.on_substation and sw1.ison and sw2.ison:
            raise ValueError(LinkError.SUBSTATION_LINKING)

        self._link = set([sw1, sw2])

    @property
    def switches(self) -> Tuple[Switch, Switch]:
        link = sorted(tuple(self._link), key=lambda sw: sw.name)
        return (link[0], link[1])

    @property
    def ison(self) -> bool:
        return self.switches[0].ison and self.switches[1].ison

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, _Link):
            return self.switches == __o.switches
        return False

    def __hash__(self) -> int:
        return hash(self.switches)


_LinkSet = Set[_Link]


class System:
    def __init__(self) -> None:
        self.__switches: _SetSw = set()
        self._links: _LinkSet = set()

    def link(self, sw1: Switch, sw2: Switch) -> None:
        self.__switches.add(sw1)
        self.__switches.add(sw2)
        self._links.add(_Link(sw1, sw2))

    def __switches_connected(self, sw: Switch) -> Iterable[Switch]:
        for link in self._links:
            if not link.ison:
                continue
            if sw not in link.switches:
                continue

            yield (_sw for _sw in link.switches if _sw != sw).__next__()

    @property
    def ismeshed(self) -> bool:
        number_switches_on = sum(1 for sw in self.__switches if sw.ison)
        number_link_on = sum(1 for link in self._links if link.ison)
        return not (number_link_on == (number_switches_on - 1))

    # @property
    # def is_substations_connected(self) -> bool:
    #     for sw in self.__switches:

    #     return False

    # @property
    # def ismeshed(self) -> bool:
