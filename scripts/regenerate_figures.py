#!/usr/bin/env python3
"""Run only the two figure functions used in r53, without changing frozen files."""
import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / 'papers/http-session-noms/figures'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'build/figures')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    load('pipeline', SOURCES / 'fig1_r48.py').fig_scoping_words(str(args.out))
    module = load('coverage', SOURCES / 'make_figures_en.r13.py')
    module.OUT = str(args.out)
    module.fig_stops(str(ROOT))


if __name__ == '__main__':
    main()
