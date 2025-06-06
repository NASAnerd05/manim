"""Set the global config and logger."""

from __future__ import annotations

import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from .cli_colors import parse_cli_ctx
from .logger_utils import make_logger
from .utils import ManimConfig, ManimFrame, make_config_parser

__all__ = [
    "logger",
    "console",
    "error_console",
    "config",
    "frame",
    "tempconfig",
    "cli_ctx_settings",
]

parser = make_config_parser()

# Logger usage: accessible globally as `manim.logger` or via `logging.getLogger("manim")`.
# For printing, use `manim.console.print()` instead of the built-in `print()`.
# For error output, use `error_console`, which prints to stderr.
logger, console, error_console = make_logger(
    parser["logger"],
    parser["CLI"]["verbosity"],
)
cli_ctx_settings = parse_cli_ctx(parser["CLI_CTX"])
# TODO: temporary to have a clean terminal output when working with PIL or matplotlib
logging.getLogger("PIL").setLevel(logging.INFO)
logging.getLogger("matplotlib").setLevel(logging.INFO)

config = ManimConfig().digest_parser(parser)
# TODO: to be used in the future - see PR #620
# https://github.com/ManimCommunity/manim/pull/620
frame = ManimFrame(config)


# This has to go here because it needs access to this module's config
@contextmanager
def tempconfig(temp: ManimConfig | dict[str, Any]) -> Generator[None, None, None]:
    """Temporarily modifies the global ``config`` object using a context manager.

    Inside the ``with`` statement, the modified config will be used.  After
    context manager exits, the config will be restored to its original state.

    Parameters
    ----------
    temp
        Object whose keys will be used to temporarily update the global
        ``config``.

    Examples
    --------

    Use ``with tempconfig({...})`` to temporarily change the default values of
    certain config options.

    .. code-block:: pycon

       >>> config["frame_height"]
       8.0
       >>> with tempconfig({"frame_height": 100.0}):
       ...     print(config["frame_height"])
       100.0
       >>> config["frame_height"]
       8.0

    """
    global config
    original = config.copy()

    temp = {k: v for k, v in temp.items() if k in original}

    # In order to change the config that every module has access to, use
    # update(), DO NOT use assignment.  Assigning config = some_dict will just
    # make the local variable named config point to a new dictionary, it will
    # NOT change the dictionary that every module has a reference to.
    config.update(temp)
    try:
        yield
    finally:
        config.update(original)  # update, not assignment!
