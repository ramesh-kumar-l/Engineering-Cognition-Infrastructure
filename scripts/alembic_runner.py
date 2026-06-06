#!/usr/bin/env python3
"""Lightweight Alembic runner that uses the alembic Python API.

This avoids spawning the `alembic` entry-point executable which may be
blocked by Application Control policies on some Windows environments.

Usage examples:
  python scripts/alembic_runner.py upgrade -c packages/storage/alembic.ini head
  python scripts/alembic_runner.py revision -c packages/storage/alembic.ini --autogenerate -m "msg"
"""

from __future__ import annotations

import sys
from typing import List

from alembic.config import Config
import alembic.command


def _parse_args(argv: List[str]) -> tuple[str, str, List[str]]:
    # Simple parsing: look for -c <config> then action and remaining args
    cfg_path = None
    args = list(argv)
    if "-c" in args:
        i = args.index("-c")
        if i + 1 < len(args):
            cfg_path = args[i + 1]
            del args[i : i + 2]
    if cfg_path is None:
        cfg_path = "alembic.ini"
    if not args:
        print("Usage: scripts/alembic_runner.py <action> [-c <alembic.ini>] [action-args...]")
        sys.exit(2)
    action = args[0]
    rest = args[1:]
    return cfg_path, action, rest


def main() -> None:
    cfg_path, action, rest = _parse_args(sys.argv[1:])
    cfg = Config(cfg_path)
    try:
        if action == "upgrade":
            target = rest[0] if rest else "head"
            alembic.command.upgrade(cfg, target)
        elif action == "downgrade":
            target = rest[0] if rest else "-1"
            alembic.command.downgrade(cfg, target)
        elif action == "revision":
            # pass through any flags (e.g. --autogenerate -m "msg")
            alembic.command.revision(cfg, *rest)
        elif action == "current":
            alembic.command.current(cfg)
        elif action == "history":
            alembic.command.history(cfg)
        else:
            print(f"Unsupported action: {action}")
            sys.exit(2)
    except Exception as exc:  # pragma: no cover - runtime helper
        print("ERROR", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
