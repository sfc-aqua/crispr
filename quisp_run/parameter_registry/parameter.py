from enum import Enum
from typing import (
    List,
    TypeVar,
    Generic,
    Optional,
    Any,
    Tuple,
    Union,
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
