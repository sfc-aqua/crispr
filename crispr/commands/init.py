import click, os
from crispr.utils import console, error_console, logger
from crispr.constants import CRISPR_TEMPALTE_PARAMETERS_TOML
from crispr.parameter_registry import ParameterRegistry


@click.command()
@click.option(
    "--output",
    "-o",
    default="simulation.plan",
    type=click.Path(exists=False),
    help="path to the output file",
)
@click.option("--force", "-f", default=False, is_flag=True, help="overwrite existing file")
@click.option(
    "--parameter-schema",
    type=click.Path(exists=True),
    default=CRISPR_TEMPALTE_PARAMETERS_TOML,
    help="path to the parameter schema toml file",
)
def init(output: str, parameter_schema: str, force: bool):
    """Generate a new simulation plan."""
    console.print(f"[green]Generating a new simulation plan at {output}")
    if not force and os.path.exists(output):
        error_console.print(
            f"[red]{output} already exists. specify a different output file with -o option or overwrite with -f option."
        )
        exit(1)

    registry = ParameterRegistry()
    with open(parameter_schema, "rt") as f:
        param_toml = f.read()
        registry.load_from_toml(param_toml)
    configs = registry.create_default_config_vars(fill_default=True)
    logger.debug(f"default config dict: {configs}")
    source = """
# -*- mode: py; -*-
# simulation plan
# you can use "range()", "list()", "filter()" and "map()" to generate simulation settings

    """
    for name in configs:
        source += f"{name} = {configs[name].__repr__()}\n"
    logger.debug(f"generated: \n{source}")

    with open(output, "wt") as f:
        f.write(source)
