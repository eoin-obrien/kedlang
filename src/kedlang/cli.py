import argparse
import logging
import os
import signal
import sys
from typing import List

from kedlang import __version__
from kedlang.exceptions import BaseKedException

from .interpreter import KedInterpreter
from .lexer import KedLexer
from .parser import KedParser

__author__ = "Eoin O'Brien"
__copyright__ = "Eoin O'Brien"
__license__ = "gpl3"

_logger = logging.getLogger(__name__)


def sigint_handler(signum, frame):
    exit(1)


signal.signal(signal.SIGINT, sigint_handler)


def file_path(value):
    if os.path.isfile(value):
        return value
    else:
        raise FileNotFoundError(value)


def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse command line parameters"""
    parser = argparse.ArgumentParser(description="kedlang")
    parser.add_argument(
        "--version", action="version", version="kedlang {ver}".format(ver=__version__)
    )
    parser.add_argument(dest="file", help="source file to execute", type=file_path)
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    lexer = KedLexer()
    parser = KedParser()
    interpreter = KedInterpreter(lexer, parser, cwd=args.file)
    with open(args.file) as f:
        code = f.read()

    try:
        interpreter.interpret(code)
    except BaseKedException as exc:
        sys.exit(f"{exc.__class__.__name__}: {exc.message}")


def run():
    """Entry point for console_scripts"""
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
