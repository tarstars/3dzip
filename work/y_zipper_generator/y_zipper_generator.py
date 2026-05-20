#!/usr/bin/env python3
"""Compatibility wrapper for the v0 top-level command name."""

from yzipper.cli import main


if __name__ == "__main__":
    raise SystemExit(main())

