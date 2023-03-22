from abc import abstractmethod, ABC
from copy import copy
from enum import Enum, auto
from typing import Iterable, List, Optional, Set, Tuple


class LinkError(Enum):
    SELF_LINKING = auto()
    SUBSTATION_LINKING = auto()


class SwitchingError(Enum):
    OFFLOAD_SWITCHING_ON_LOAD = auto()
    CAUSES_MESH = auto()
    CAUSES_SUBSTATIONS_INTERCONNECTION = auto()
    SYSTEM_NOT_DEFINED = auto()


class SCHGError(Exception):
    pass


class State(Enum):
    ON = 1
    OFF = 0

    def __repr__(self) -> str:
        if self == State.ON:
            return "ON"
        else:
            return "OFF"

    def __str__(self) -> str:
        return self.__repr__()


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
    @abstractmethod
    def _state(self) -> State:
        """Don't use it. Use sw.state instead"""
        ...

    @_state.setter
    @abstractmethod
    def _state(self, state: State) -> None:
        """Don't use it. Use sw.togle_state() instead"""
        ...

    @property
    @abstractmethod
    def sys(self) -> Optional["System"]:
        ...

    @sys.setter
    @abstractmethod
    def sys(self, sys: "System") -> None:
        ...

    @property
    def ison(self) -> bool:
        return bool(self.state.value)

    @abstractmethod
    def togle_state(self) -> None:
        ...

    def _notify(self) -> List[SwitchingError]:
        if self.sys is None:
            return [SwitchingError.SYSTEM_NOT_DEFINED]
        return self.sys.inform_change(self)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Switch):
            return self.name == __o.name
        return False

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"SW({self.name}, {self.state})"

    def __str__(self) -> str:
        return self.__repr__()


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
        self._sys: Optional["System"] = None

    @property
    def on_substation(self) -> bool:
        return self._on_substation

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> State:
        return self.__state

    @property
    def _state(self) -> State:
        return self.__state

    @_state.setter
    def _state(self, state: State) -> None:
        self.__state = state

    @property
    def sys(self) -> Optional["System"]:
        return self._sys

    @sys.setter
    def sys(self, sys: "System") -> None:
        self._sys = sys

    def togle_state(self) -> None:
        erros = self._notify()
        if len(erros) > 0:
            raise SCHGError(erros)
        self.__state = State(not self.__state.value)


class OffLoad(Switch):
    def __init__(
        self,
        name: str,
        initial_state: State,
    ) -> None:
        self.__name = name
        self.__state = initial_state
        self._sys: Optional["System"] = None

    @property
    def on_substation(self) -> bool:
        return False

    @property
    def name(self) -> str:
        return self.__name

    @property
    def state(self) -> State:
        return self.__state

    @property
    def _state(self) -> State:
        return self.__state

    @_state.setter
    def _state(self, state: State) -> None:
        self.__state = state

    @property
    def sys(self) -> Optional["System"]:
        return self._sys

    @sys.setter
    def sys(self, sys: "System") -> None:
        self._sys = sys

    def togle_state(self) -> None:
        """Try to toggle the switch

        Raises:
            SCHGError: Raises when some SwitchingError occurs
        """
        erros = self._notify()
        if len(erros) > 0:
            raise SCHGError(erros)
        self.__state = State(not self.__state.value)


class Link:
    def __init__(self, sw1: Switch, sw2: Switch) -> None:
        if sw1 == sw2:
            raise SCHGError([LinkError.SELF_LINKING])

        if sw1.on_substation and sw2.on_substation and sw1.ison and sw2.ison:
            raise SCHGError([LinkError.SUBSTATION_LINKING])

        self._link = set([sw1, sw2])

    @property
    def switches(self) -> Tuple[Switch, Switch]:
        link = sorted(tuple(self._link), key=lambda sw: sw.name)
        return (link[0], link[1])

    @property
    def ison(self) -> bool:
        return self.switches[0].ison and self.switches[1].ison

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Link):
            return self.switches == __o.switches
        return False

    def __hash__(self) -> int:
        return hash(self.switches)

    def __repr__(self) -> str:
        sw1, sw2 = self.switches
        return f"Link({sw1.name}, {sw2.name})"

    def __str__(self) -> str:
        return self.__repr__()


LinkSet = Set[Link]


class System:
    def __init__(self) -> None:
        self.__switches: _SetSw = set()
        self._links: LinkSet = set()

    def link(self, sw1: Switch, sw2: Switch) -> None:
        """Link two switches

        Args:
            sw1 (Switch): Switch 1
            sw2 (Switch): Switch 2
        Raises:
            SCHGError: Raises when some LinkError occurs
        """

        self.__switches.add(sw1)
        self.__switches.add(sw2)
        self._links.add(Link(sw1, sw2))
        sw1.sys = self
        sw2.sys = self

    @property
    def links(self) -> List[Link]:
        return sorted(
            self._links,
            key=lambda link: link.switches[0].name + link.switches[1].name,
        )

    def __switches_connected(self, sw: Switch) -> Iterable[Switch]:
        for link in self.links:
            if not link.ison:
                continue
            if sw not in link.switches:
                continue

            sw1, sw2 = link.switches
            next_sw = sw1 if sw1 != sw else sw2

            yield next_sw

    @property
    def swicthes(self) -> List[Switch]:
        return sorted(self.__switches, key=lambda sw: sw.name)

    @property
    def ismeshed(self) -> bool:
        number_switches_on = sum(1 for sw in self.swicthes if sw.ison)
        number_link_on = sum(1 for link in self.links if link.ison)
        return not (number_link_on == (number_switches_on - 1))

    @property
    def is_substations_connected(self) -> bool:
        for sw in self.swicthes:
            if self.__substations_connected(sw, allowed=1):
                return True

        return False

    def __substations_connected(
        self,
        sw: Switch,
        allowed: int,
        count: int = 0,
        visited: Optional[List[Switch]] = None,
    ) -> bool:
        if visited is None:
            visited = []
        visited.append(sw)
        if sw.on_substation:
            count += 1

        if count > allowed:
            return True

        sws = self.__switches_connected(sw)

        for next_sw in sws:
            if next_sw == sw:
                continue
            if next_sw in visited:
                continue
            if self.__substations_connected(next_sw, allowed, count, visited):
                return True

        return False

    def offload_trying_on_load(self, sw: Switch) -> bool:
        if not isinstance(sw, OffLoad):
            return False

        initial_state = copy(sw._state)
        if initial_state == State.OFF:
            sw._state = State.ON

        value = self.__substations_connected(sw, allowed=0)
        sw._state = initial_state
        return value

    def inform_change(self, sw: Switch) -> List[SwitchingError]:
        state_initial = copy(sw.state)
        sw._state = State(not sw.state.value)

        error = []
        if self.ismeshed:
            error.append(SwitchingError.CAUSES_MESH)

        if self.is_substations_connected:
            error.append(SwitchingError.CAUSES_SUBSTATIONS_INTERCONNECTION)

        if self.offload_trying_on_load(sw):
            error.append(SwitchingError.OFFLOAD_SWITCHING_ON_LOAD)

        sw._state = state_initial

        return error
