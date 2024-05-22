from __future__ import annotations

from src.vrc_osc import OSCValueType


class AvatarParam:
    def __init__(self):
        super().__init__()
        # default values for json data
        self.name = ""
        self.translation = ""
        self.input_address = ""
        self.output_address = ""
        self.osc_type = OSCValueType.UNDEFINED
        self.value: int | float | bool = 0.0
        self.selected: bool = False

    def load_from_json(self, json_data):
        if j_name := json_data.get('name'):
            self.name = j_name
        if j_input := json_data.get('input'):
            if j_in_add := j_input.get('address'):
                self.input_address = j_in_add
            if j_in_type := j_input.get('type'):
                self.osc_type = j_in_type
        if j_output := json_data.get('output'):
            if j_out_addr := j_output.get('address'):
                self.output_address = j_out_addr
            if j_out_type := j_output.get('type'):
                self.osc_type = j_out_type

        # calculate values
        self.value = {
            OSCValueType.INT: int(0),
            OSCValueType.FLOAT: 0.0,
            OSCValueType.BOOL: False
        }.get(self.osc_type, 0.0)
