#!/usr/bin/env python3
"""Generator: required-only variant. Same shape but no NotRequired."""

import sys
from pathlib import Path


def gen(n_variants: int, n_keys: int) -> str:
    out = ['from typing import TypedDict, Literal\n']
    optional_types = ["str", "int", "bool", "list[str]", "dict[str, str]"]

    names = []
    for i in range(n_variants):
        name = f"T{i}"
        names.append(name)
        out.append(f"\n\nclass {name}(TypedDict):")
        out.append(f'    type: Literal["t{i}"]')
        for k in range(n_keys):
            t = optional_types[k % len(optional_types)]
            out.append(f"    k{k}: {t}")  # required

    out.append("\n\nU = (")
    for i, n in enumerate(names):
        sep = "" if i == 0 else " | "
        out.append(f"    {sep}{n}")
    out.append(")\n")
    out.append("\n\ndef use(v: U) -> None:")
    out.append("    _ = dict(v)\n")
    return "\n".join(out)


if __name__ == "__main__":
    n = int(sys.argv[1])
    k = int(sys.argv[2])
    out_path = Path(sys.argv[3])
    out_path.write_text(gen(n, k))
