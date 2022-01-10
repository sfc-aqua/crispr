from typing import List, Dict, Any, Optional
import toml
from crispr.parameter_registry.schema import PARAM_SCHEMA_SCHEMA
from crispr.utils import error_console, logger
from .parameter import Parameter, ParameterKind
from .schema import validate_config


class ParameterRegistry:
    parameters: List[Parameter]

    def __init__(self) -> None:
        self.parameters = []
        init_registry(self)

    @staticmethod
    def extract_config(source_str: str) -> List[Parameter]:
        conf = toml.loads(source_str)
        logger.debug(conf)
        if not validate_config(conf):
            raise RuntimeError("Invalid config")
        param_data = conf["parameter"]
        return [Parameter.from_dict(key, param_data[key]) for key in param_data]

    def register(self, parameter: Parameter):
        if [p for p in self.parameters if p == parameter]:
            return
        for p in self.parameters:
            if p.singular == parameter.singular:
                error_console.print(
                    f"[yellow]warning: {p.singular} is already registered, override parameter definition"
                )
                self.parameters.remove(p)
                break
        if not parameter.validate():
            raise RuntimeError(f"Invalid parameter: {parameter}")
        self.parameters.append(parameter)

    def register_all(self, parameters: List[Parameter]):
        for p in parameters:
            self.register(p)

    def create_default_config_vars(self, fill_default: bool = False) -> Dict[str, Any]:
        vars = dict()
        for parameter in self.parameters:
            k, v = parameter.default_key_value()
            if fill_default:
                vars[k] = v
            else:
                vars[k] = None
        vars["config_ini_file"] = self.find_by_name("config_ini_file").default_value
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
                if not parameter.plural and parameter.plural in vars:
                    error_console.print(
                        f"[red]error: both {parameter.singular} and {parameter.plural} are used. Only one is allowed"
                    )
                    is_valid = False
            elif parameter.plural and parameter.plural in vars:
                key = parameter.plural
                if not parameter.validate_type(key, vars[key]):
                    is_valid = False

        for key in vars:
            if not self.find_by_name_or_none(key):
                error_console.print(f"[yellow]warning: {key} is not registered, ignoring")

        return is_valid

    def load_from_toml(self, source_str: str) -> None:
        self.register_all(self.extract_config(source_str))

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
        raise RuntimeError(f"Parameter {name} is not registered")

    def find_by_name_or_none(self, name: str) -> Optional[Parameter]:
        for p in self.parameters:
            if name == p.singular:
                return p
            if p.plural and name == p.plural:
                return p
        return None


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
        Parameter[str](
            singular="network_type",
            plural="network_types",
            kind=ParameterKind.BUILT_IN,
            default_values=["linear"],
            required=True,
            options=["linear"],
        )
    )

    registry.register(
        Parameter[str](
            singular="config_ini_file",
            plural=None,
            kind=ParameterKind.BUILT_IN,
            default_value="${CRISPR_ROOT_DIR}/config/omnetpp.ini",
            required=True,
        )
    )

    return registry
