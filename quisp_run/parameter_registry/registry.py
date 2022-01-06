from typing import List, Dict, Any
from quisp_run.utils import error_console
from .parameter import Parameter, ParameterKind


class ParameterRegistry:
    parameters: List[Parameter]

    def __init__(self) -> None:
        self.parameters = []

    def register(self, parameter: Parameter):
        if [p for p in self.parameters if p == parameter]:
            return
        if not parameter.validate():
            raise RuntimeError(f"Invalid parameter: {parameter}")
        self.parameters.append(parameter)

    def create_default_config_vars(self) -> Dict[str, Any]:
        vars = dict()
        for parameter in self.parameters:
            k, v = parameter.default_key_value()
            vars[k] = v
        return vars

    def validate_config_vars(self, vars: Dict[str, Any]) -> bool:
        is_valid = True
        for parameter in self.parameters:
            if parameter.required:
                if parameter.singular not in vars and parameter.plural not in vars:
                    error_console.print(
                        f"[red]error: {parameter.singular or parameter.plural} is required"
                    )
                    is_valid = False

                key = parameter.singular
                if key and key in vars:
                    if not parameter.validate_type(key, vars[key]):
                        is_valid = False

                key = parameter.plural
                if key and key in vars:
                    if not parameter.validate_type(key, vars[key]):
                        is_valid = False
        return is_valid

    def get_singular_name(self, singular_or_plural_name: str) -> str:
        for p in self.parameters:
            if singular_or_plural_name == p.plural:
                if p.singular:
                    return p.singular
                if p.plural:
                    return p.plural
            if p.singular and singular_or_plural_name == p.singular:
                return p.singular
        raise RuntimeError(f"{singular_or_plural_name} is not registered")

    def find_by_name(self, name: str) -> Parameter:
        for p in self.parameters:
            if name == p.singular:
                return p
        raise RuntimeError("Parameter {name} is not registered")


def init_registry(registry: ParameterRegistry) -> ParameterRegistry:
    registry.register(
        Parameter[str](
            singular="title",
            plural=None,
            kind=ParameterKind.META,
            default_value="",
            required=True,
        )
    )
    registry.register(
        Parameter[int](
            singular="num_buf",
            plural="num_bufs",
            kind=ParameterKind.PARAM,
            default_values=[50],
            required=True,
            param_key="buffers",
        )
    )
    registry.register(
        Parameter[int](
            singular="num_node",
            plural="num_nodes",
            kind=ParameterKind.NETWORK_PARAM,
            default_values=[5],
            required=True,
            param_key="numNodes",
        )
    )
    registry.register(
        Parameter[str](
            singular="network_type",
            plural="network_types",
            kind=ParameterKind.BUILT_IN,
            default_value="linear",
            required=True,
            options=["linear"],
        )
    )
    registry.register(
        Parameter[str](
            singular="connection_type",
            plural="connection_types",
            kind=ParameterKind.NETWORK_PARAM,
            default_value=None,
            required=True,
            options=["MIM", "MM"],
            param_key="connectionType",
        )
    )
    registry.register(
        Parameter[str](
            singular="config_ini_file",
            plural=None,
            kind=ParameterKind.BUILT_IN,
            default_value="${QUISP_RUN_ROOT_DIR}/config/omnetpp.ini",
            required=True,
        )
    )
    registry.register(
        Parameter[int](
            singular="traffic_pattern_index",
            plural="traffic_pattern_indices",
            kind=ParameterKind.PARAM,
            default_values=[0],
            required=True,
            param_key="app.TrafficPattern",
        )
    )
    registry.register(
        Parameter[int](
            singular="lone_initiator_addr",
            plural="lone_initiator_addrs",
            kind=ParameterKind.PARAM,
            default_values=[0],
            required=True,
            param_key="app.LoneInitiatorAddress",
        )
    )
    registry.register(
        Parameter[bool](
            singular="link_tomography_enabled",
            plural="link_tomography_enabled_list",
            kind=ParameterKind.PARAM,
            default_values=[False],
            required=True,
            param_key="qrsa.hm.link_tomography",
        )
    )
    registry.register(
        Parameter[int](
            singular="num_purification_iteration",
            plural="num_purification_iterations",
            kind=ParameterKind.PARAM,
            default_values=[0],
            required=True,
            param_key="qrsa.hm.initial_purification",
        )
    )
    registry.register(
        Parameter[int](
            singular="purification_type",
            plural="purification_types",
            kind=ParameterKind.PARAM,
            default_values=[1001],
            required=True,
            param_key="qrsa.hm.Purification_type",
        )
    )
    return registry
