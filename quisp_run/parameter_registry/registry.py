from enum import Enum
from typing import (
    List,
    TypeVar,
    Generic,
    Optional,
    Dict,
    Any,
    Tuple,
    Union,
    get_origin,
    get_args,
    get_type_hints,
)
from dataclasses import dataclass
from quisp_run.utils import error_console


class ParameterKind(Enum):
    FIXED = 1
    SIM_ARG = 2


T = TypeVar("T")


@dataclass
class Parameter(Generic[T]):
    singular: Optional[str]
    plural: Optional[str]
    kind: ParameterKind
    required: bool
    default_value: Optional[T] = None
    default_values: Optional[List[T]] = None
    options: Optional[List[T]] = None

    @property
    def required_to_fill(self) -> bool:
        return self.default_value is None

    def validate(self) -> bool:
        if self.singular is None and self.plural is None:
            error_console.print("[red]error: Parameter.singular and Parameter.plural are both None")
            return False
        return True

    def default_key_value(self) -> Tuple[str, Optional[Union[T, List[T]]]]:
        if self.singular is not None:
            if self.plural is not None:
                return self.plural, self.default_values
            return self.singular, self.default_value
        assert False, f"Unexpected case: {self}"

    def __str__(self):
        return f"{self.singular or self.plural}: default({self.default_value}), required({self.required}) {self.kind}"

    @property
    def name(self):
        if self.singular is not None:
            if self.plural is not None:
                return f"{self.singular} or {self.plural}"
            return self.singular
        if self.plural is not None:
            return self.plural
        assert False, f"Unexpected case: {self}"

    def validate_type(self, key: str, value: Any) -> bool:
        # https://stackoverflow.com/questions/60584388/how-to-check-typevars-type-at-runtime
        t = self.__orig_class__.__args__[0]  # type: ignore
        if key == self.singular:
            return isinstance(value, t)
        if key == self.plural:
            isinstance(value, list)
            return isinstance(value, list) and all(isinstance(v, t) for v in value)
        raise RuntimeError(f"Parameter error: {self}")


class ParameterRegistry:
    parameters: List[Parameter] = []

    def register(self, parameter: Parameter):
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
        return is_valid


registry: ParameterRegistry = ParameterRegistry()


def init_registry():
    global registry
    registry = ParameterRegistry()
    registry.register(
        Parameter(
            singular="num_buf",
            plural="num_bufs",
            kind=ParameterKind.FIXED,
            default_value=[],
            required=True,
        )
    )
    registry.register(
        Parameter[int](
            singular="num_node",
            plural="num_nodes",
            kind=ParameterKind.FIXED,
            default_values=[5],
            required=True,
        )
    )
    registry.register(
        Parameter[str](
            singular="network_type",
            plural="network_types",
            kind=ParameterKind.FIXED,
            default_value="linear",
            required=True,
            options=["linear"],
        )
    )
    registry.register(
        Parameter[str](
            singular="connection_type",
            plural="connection_types",
            kind=ParameterKind.FIXED,
            default_value=None,
            required=True,
            options=["MIM", "MM"],
        )
    )
    registry.register(
        Parameter[str](
            singular="config_ini_file",
            plural=None,
            kind=ParameterKind.FIXED,
            default_value="",
            required=True,
        )
    )
