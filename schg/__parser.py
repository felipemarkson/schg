from typing import Callable, Dict, List, Optional, Type, Union
from .__base import OffLoad, OnLoad, State, Switch
from dataclasses import dataclass
from os import path as pathfunc

TAG = "schg:"
OFF_LOAD_TAG = "offload"
ON_LOAD_TAG = "onload"

SUB_TAG = "substation"

ON_TAG = "on"
OFF_TAG = "off"

END_TAG = ";"


def redirect_handler(path: str) -> List[str]:
    """
    If a redirect command is found, call the function recursively
    Args:
        path: The path to the file.
        acc: A buffer to store the commands.
    Returns:
        True if the file has a solve command.
    """
    with open(path, "rt") as file:
        lines = file.readlines()

    commands = __remove_comments_dss(lines)
    no_redirect_cmds = []

    for line in commands:
        if "redirect" in line.lower().strip():
            cmd = " ".join(line.split(" ")[1:]).strip()
            head = pathfunc.split(path)[0]
            no_redirect_cmds += redirect_handler(pathfunc.join(head, cmd))
        else:
            no_redirect_cmds.append(line)

    return no_redirect_cmds


def __remove_comments_dss(list_cmd: List[str]) -> List[str]:
    vanished: List[str] = []
    in_a_comment = False
    for cmd in list_cmd:
        if cmd.strip().startswith("/*"):
            in_a_comment = True
            continue
        elif cmd.strip().endswith("*/"):
            in_a_comment = False
            continue
        if in_a_comment:
            continue
        elif cmd.strip().startswith("!"):
            continue
        elif cmd.strip().startswith("//"):
            continue
        elif len(cmd.strip()) == 0:
            continue

        if cmd.strip().startswith("~"):
            vanished[-1] += cmd.strip()[1:]
        else:
            vanished.append(cmd.strip())

    return vanished


# def __is_line(cmd: str) -> bool:
#     is_line = False
#     for data in cmd.lower().split():
#         if "line." in data:
#             is_line = True
#             break
#     return ("new" in cmd.lower().split()) and is_line


@dataclass
class __Raw:
    type_sw: Type[Union[OnLoad, OffLoad]]
    name: str
    state: State
    onsub: bool
    links: List[str]
    cmd: str


def __get_definition(
    cmd: str, getname_func: Callable[[str], str], is_dss: bool = True
) -> Optional[__Raw]:
    try:
        name = getname_func(cmd)
        if is_dss:
            tags = cmd.lower().strip().split(TAG)[1].split()

    except IndexError:
        return None

    type_sw = tags[0]
    sw_type: Optional[Type[Switch]] = None
    if type_sw == OFF_LOAD_TAG:
        sw_type = OffLoad
    elif type_sw == ON_LOAD_TAG:
        sw_type = OnLoad
    else:
        raise ValueError(f"Switch type not founded on :{cmd}")

    state = tags[1]
    sw_state: Optional[State] = None
    if state == ON_TAG:
        sw_state = State.ON
    elif state == OFF_TAG:
        sw_state = State.OFF
    else:
        raise ValueError(f"Switch state not founded on :{cmd}")

    link_index = 2
    onsub = False
    if tags[2] == SUB_TAG:
        link_index += 1
        if type_sw == OFF_LOAD_TAG:
            raise ValueError(f"Switch type {OFF_LOAD_TAG} is on substation :{cmd}")
        onsub = True

    links = []
    for link in tags[link_index:]:
        if link.endswith(";"):
            links.append(link[:-1])
            break
        if link == ";":
            break
        links.append(link)

    return __Raw(sw_type, name, sw_state, onsub, links, cmd)


def get_raws(
    list_cmd: List[str], getname_func: Callable[[str], str]
) -> Dict[str, __Raw]:
    __raws: Dict[str, __Raw] = {}
    for cmd in list_cmd:
        __raw = __get_definition(cmd, getname_func)
        if __raw is None:
            continue
        __raws[__raw.name] = __raw

    for __raw in __raws.values():
        for sw in __raw.links:
            if sw not in __raws.keys():
                raise ValueError(f"Switch {sw} not found in link: {__raw.cmd}")

    return __raws
