from __future__ import annotations

import json
from typing import Any, Callable

from src.vrc_osc.vrc_osc import OSCValueType, OscMessage, VrcOscService


class Avatar:
    def __init__(self, osc_service: VrcOscService):
        self.param_map: dict[str, AvatarParam] = dict()
        self.osc_map: dict[str, AvatarParam] = dict()
        self.avatar_id: str = ""
        self.avatar_name: str = ""
        self.osc_service = osc_service

    def load_vrchat_osc_file(self, filename):
        with open(filename, 'r', encoding='utf-8-sig') as file:
            j = json.load(file)
            if j_name := j.get('name'):
                self.avatar_name = j_name
            if j_id := j.get('id'):
                self.avatar_id = j_id
            for j_param in j["parameters"]:
                param = AvatarParam(self)
                param.load_vrchat_osc_file(j_param)
                if param.name:
                    self.param_map[param.name] = param
                if param.output_address:
                    self.osc_map[param.output_address] = param

    def receive_osc_message(self, osc_msg: OscMessage) -> None:
        osc_path, _, osc_value = osc_msg
        if param := self.osc_map.get(osc_path):
            param.receive_osc_value(osc_value)


class AvatarParam:
    """
    Holds values from the VRChat generated OSC info files. Names are based on the property names used in the file,
    so in/out is from the view of VRChat.
    """
    def __init__(self, avatar: Avatar) -> None:
        super().__init__()
        self.avatar = avatar
        # default values for json data
        self.name = ""
        """This is the name of the property as defined during avatar making."""
        self.translation = ""
        """This value is generated by the program and not provided by VRChat"""
        self.input_address = ""
        """
        [Can be empty string]
        This is the OSC path to send to VRChat. If it is empty, then VRC doesn't accept OSC messages for it. Currently,
        this means that this avatar parameter is not defined by the avatar creator, but created by the system.
        This includes basic avatar properties like moving around and all physbone derived parameters like _isGrabbed
        """
        self.output_address = ""
        """
        [Can be empty string]
        This is the OSC path to receive updates from VRChat.
        """
        self.osc_type = OSCValueType.UNDEFINED
        self.osc_input_type = OSCValueType.UNDEFINED
        """Read from the VRChat json. Use osc_type instead."""
        self.osc_output_type = OSCValueType.UNDEFINED
        """Read from the VRChat json. Use osc_type instead."""
        self._value: int | float | bool = 0.0
        self.selected: bool = False
        self.subscriber: set[Callable[[Any], None]] = set()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: bool | float | bool):
        coerced_value = self._coerce(value)
        if coerced_value == self._value:
            return
        self._value = coerced_value
        self.avatar.osc_service.send(self.output_address, self.osc_type, value)
        self._notify_subscriber()

    def subscribe(self, subscriber: Callable[[Any], None]) -> None:
        self.subscriber.add(subscriber)

    def unsubscribe(self, subscriber: Callable[[Any], None]) -> None:
        self.subscriber.remove(subscriber)

    def _notify_subscriber(self):
        for s in self.subscriber:
            try:
                s(self._value)
            except Exception as e:
                print(f"During notifying subscribers of {self.name}, an exception occured: {e}")

    def receive_osc_value(self, value: Any):
        coerced = self._coerce(value)
        self._value = coerced
        self._notify_subscriber()

    def load_vrchat_osc_file(self, json_data):
        # osc_type is the only non-trivial resolved value
        if j_name := json_data.get('name'):
            self.name = j_name
        if j_input := json_data.get('input'):
            if j_in_add := j_input.get('address'):
                self.input_address = j_in_add
            if j_in_type := j_input.get('type'):
                self.osc_type = j_in_type
                self.osc_input_type = j_in_type
        if j_output := json_data.get('output'):
            if j_out_addr := j_output.get('address'):
                self.output_address = j_out_addr
            if j_out_type := j_output.get('type'):
                self.osc_type = j_out_type
                self.osc_output_type = j_out_type

        self._value = self._coerce(0)
        self._verify()

    def _coerce(self, new_value: Any) -> bool | float | int:
        """
        Convert the value to the type of this avatar parameter.
        :param new_value: New value that can be of a different type
        :return: None
        """
        try:
            match self.osc_type:
                case OSCValueType.INT:
                    return int(new_value)
                case OSCValueType.FLOAT:
                    return float(new_value)
                case OSCValueType.BOOL:
                    return bool(new_value)
        except Exception as e:
            print(f"Trying to coerce value {str(new_value)} into {self.osc_type} threw Error {str(e)}")

    def _verify(self):
        """
        Sanity check cetain assumptions about a parameter
        1. It has a name
        2. It has an output address
        3. If it has both input and output defined, their types should match.
        This function is a canary for future vrchat updates
        :return:
        """
        if not self.name:
            print("OSC parameter doesn't have a name")
        if not self.output_address:
            # note it's normal that certain parameter do not have an input address.
            # however, everything should be output by vrchat.
            print("OSC parameter doesn't have a output address.")
        if self.osc_input_type and self.osc_output_type:
            if self.osc_input_type != self.osc_input_type:
                print("Input and output types do not match for OSC parameter.")