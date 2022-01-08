from enum import Enum
from typing import (
    List,
    TypeVar,
    Generic,
    Optional,
    Any,
    Tuple,
    Union,
    get_args,
)
from dataclasses import dataclass
from crispr.utils import error_console


class ParameterKind(Enum):
    META = 1  # meta data, not used in simulation
    BUILT_IN = 2  # built-in parameter, network_type, etc.
    NETWORK_PARAM = 3  # {network_name}.{param_name} = {param_value}
    PARAM = 4


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
    param_key: str = ""

    @property
    def required_to_fill(self) -> bool:
        return self.default_value is None

    def validate(self) -> bool:
        assert hasattr(self, "__orig_class__"), f"invalid type var for {self}"  # type: ignore
        assert len(self.__orig_class__.__args__) == 1, f"invalid type var for {self}"  # type: ignore
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
            if value is None:
                error_console.print(f'[red]plan error: "{key}" is missing')
                return False

            if not isinstance(value, t):
                error_console.print(f'[red]plan error: "{key}" is not {t.__name__}')
                return False

            return True

        if key == self.plural:
            if value is None:
                error_console.print(f'[red]plan error: "{key}" is missing')
                return False

            if not isinstance(value, list):
                error_console.print(
                    f'[red]plan error: "{key}" is not a list, should be a list of {t.__name__}'
                )
                return False

            if not all(isinstance(v, t) for v in value):
                error_console.print(
                    f'[red]plan error: "{key}" is not a list of {t.__name__}, value={value}'
                )
                return False
            return True
        raise RuntimeError(f'Parameter error: "{self}", key={key}, value={value}')

    def is_number(self) -> bool:
        return self.__orig_class__.__args__[0] is int  # type: ignore

    def is_bool(self) -> bool:
        return self.__orig_class__.__args__[0] is bool  # type: ignore
