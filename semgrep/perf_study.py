import os
from pathlib import Path
from typing import Optional

import click


def all_files(path: Path, extension: Optional[str]):
    for r, d, f in os.walk(path):
        for file in f:
            if extension is None or extension in file:
                yield os.path.join(r, file)


@click.command()
@click.option('--config')
@click.option('--files')
def perf_study(config, files):
    pass
    # all_rules =
