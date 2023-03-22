# Switch Change (schg)

_A packaged to identify problems in switching on eletricity distribution systems._

There are two types of switches:

- `OnLoad`: Which can change its the state (toggle) with energy (Eg: protection devices)
- `OffLoad`: Which can not change its the state (toggle) with energy.

When the operator try to operate these switches, the follow problems could occours:

- `OFFLOAD_SWITCHING_ON_LOAD`: Trying to switch an `OffLoad` in loading.
- `CAUSES_MESH`: The operation causes mesh in the topology.
- `CAUSES_SUBSTATIONS_INTERCONNECTION`: The operation causes interconnection between substations (Eg: short-circuit).

This packaged aims to identify this problems and report.

However, it is not fully tested yet. So, its is not ready to publishing.


## Basic usage:
```python
from schg import OnLoad, OffLoad, State, System

sw0 = OnLoad("sw0"), State.ON, on_substation=True)
sw1 = OffLoad("sw1"), State.ON)
sw2 = OnLoad("sw2"), State.OFF)
sys = System()

sys.link(sw0, sw1)
sys.link(sw1, sw2)

sw2.toggle_state() # It will raise if any problem happen.
```

## Usage from files

### For `.schg` files:

#### Syntax
`{name} {type} {state} {substation (required only for OnLoad type)} {name of switches linked}`

#### Example

In the `.schg` file:
```
sw1 OnLoad ON substation sw2 sw3
sw2 OffLoad ON sw1 sw3
sw3 OnLoad OFF substation sw2 sw1
```

In the python file:
```python
from schg import FromFile
path = "path/to/file.schg"
sys = FromFile(path)
sys.toggle_sw("sw3")  # It will raise if any problem happen.
```

### For `.dss` files:

#### Syntax
`New Line.{name}... {// or !} schg: {type} {state} {substation (required only for OnLoad type)} {name of switches linked}`
`

#### Example

In the `.dss` file:
```
New Line.SW1 Phases=3  ... // schg: OnLoad ON substation SW2
New Line.SW2 Phases=3  ... ! schg: OffLoad ON substation SW1
```

In the python file:
```python
from schg import FromFile
path = "path/to/file.dss"
sys = FromFile(path)
sys.toggle_sw("sw2")  # It will raise if any problem happen.
```

## License

Copyright 2023 Felipe M. dos S. Monteiro <fmarkson@outlook.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.