from typing import Dict
from .__base import OffLoad, Switch, System
from .__parser import get_raws
from .__parser import redirect_handler


def _get_name_dss(cmd: str) -> str:
    nonew = cmd.lower().strip().split("new")[1]
    noline = nonew.strip().split("line.")[1]
    splits = noline.split(".")[0].split()
    if len(splits) > 0:
        return splits[0]
    else:
        raise ValueError(f"No name founded on :{cmd}")


class FromDSS:
    """
    Parser from .dss files
    Ex:
        new line.name ! schg: OnLoad ON SUBSTATION  sw1name sw2name sw3name...;
        new line.name \\ schg: OnLoad ON SUBSTATION  sw1name sw2name sw3name...;
    """

    def __init__(self, path: str):
        cmds = redirect_handler(path)
        __raws = get_raws(cmds, _get_name_dss)
        self.switches: Dict[str, Switch] = {}
        self.sys = System()
        for __raw in __raws.values():
            sw = None
            if __raw.type_sw is OffLoad:
                sw = __raw.type_sw(__raw.name, __raw.state)
            else:
                sw = __raw.type_sw(
                    __raw.name,
                    __raw.state,
                    on_substation=__raw.onsub,
                )  # type: ignore
            self.switches[__raw.name] = sw

        for __raw in __raws.values():
            sw1 = self.switches[__raw.name]
            for link in __raw.links:
                sw2 = self.switches[link]
                self.sys.link(sw1, sw2)

    def togle_sw(self, name: str) -> None:
        self.switches[name.lower()].togle_state()
