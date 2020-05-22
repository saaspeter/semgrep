import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple
from typing import Optional

import semgrep.config_resolver
from semgrep.constants import PLEASE_FILE_ISSUE_TEXT
from semgrep.constants import SEMGREP_PATH
from semgrep.error import SemgrepException
from semgrep.util import print_error
from semgrep.util import print_error_exit


def dump_parsed_ast(
        to_json: bool, language: str, pattern: Optional[str], targets_str: List[str]
) -> None:
    targets = semgrep.config_resolver.resolve_targets(targets_str)
    if pattern is None and len(targets) != 1:
        print_error_exit(
            f"exactly one target file is required with this option (got {targets})"
        )
    try:
        print(parsed_ast(to_json, language, pattern, tuple(targets)))
    except subprocess.CalledProcessError as ex:
        print_error(f"error invoking semgrep with:\n\t{' '.join(pattern)}\n{ex}")
        print_error_exit(f"\n\n{PLEASE_FILE_ISSUE_TEXT}")


@lru_cache(maxsize=sys.maxsize)
def parsed_ast(
        to_json: bool, language: str, pattern: Optional[str], targets: Tuple[Path]
) -> str:
    with tempfile.NamedTemporaryFile("w") as fout:
        if pattern:
            fout.write(pattern)
            fout.flush()
            args = ["-lang", language, "-dump_pattern", fout.name]
        else:
            if len(targets) != 1:
                raise ValueError(
                    f"When pattern is not set, exactly one target file is required. (Got {targets})"
                )
            target = targets[0]
            args = ["-lang", language, "-dump_ast", str(target)]

        if to_json:
            args = ["-json"] + args

        cmd = [SEMGREP_PATH] + args
        try:
            output = subprocess.check_output(cmd, shell=False)
            return output.decode()
        except subprocess.CalledProcessError:
            print(f'Failure for pattern ({language}): "{pattern}"')
            raise
