#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from typing import List

from quisp_run.commands import run, plan, status
import logging
from quisp_run.utils import logger


@click.group()
@click.option("--debug/--no-debug", default=False)
def main(debug: bool):
    if debug:
        logger.setLevel(level=logging.DEBUG)


main.add_command(run)
main.add_command(plan)
main.add_command(status)
