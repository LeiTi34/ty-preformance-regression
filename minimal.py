"""Minimal reproducer for a severe performance regression in ty 0.0.39 vs 0.0.38.

`ty check` on this single 33-line file takes >30s on ty 0.0.39 (with the file
shape we use in production it exceeds 90s and CI cancels the step).
The same file checks in ~0.16s on ty 0.0.38.

The trigger is `dict(v)` where `v` is typed as a union of TypedDicts.
Replacing `dict(v)` with `{**v}`, `v.keys()`, `v.items()`, or `v["type"]`
makes the check finish instantly — only the `dict(...)` constructor
trips ty 0.0.39's inference into a superlinear/exponential path.

Increasing the number of union members or the number of keys per TypedDict
makes the slowdown grow rapidly.
"""

from typing import TypedDict, Literal


class T0(TypedDict):
    type: Literal["t0"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T1(TypedDict):
    type: Literal["t1"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T2(TypedDict):
    type: Literal["t2"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T3(TypedDict):
    type: Literal["t3"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T4(TypedDict):
    type: Literal["t4"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T5(TypedDict):
    type: Literal["t5"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T6(TypedDict):
    type: Literal["t6"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T7(TypedDict):
    type: Literal["t7"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T8(TypedDict):
    type: Literal["t8"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T9(TypedDict):
    type: Literal["t9"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T10(TypedDict):
    type: Literal["t10"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T11(TypedDict):
    type: Literal["t11"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T12(TypedDict):
    type: Literal["t12"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T13(TypedDict):
    type: Literal["t13"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T14(TypedDict):
    type: Literal["t14"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T15(TypedDict):
    type: Literal["t15"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T16(TypedDict):
    type: Literal["t16"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T17(TypedDict):
    type: Literal["t17"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


class T18(TypedDict):
    type: Literal["t18"]
    k0: str
    k1: int
    k2: bool
    k3: list[str]
    k4: dict[str, str]


U = (
    T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9
    | T10 | T11 | T12 | T13 | T14 | T15 | T16 | T17 | T18
)


def use(v: U) -> None:
    # `dict(v)` is the trigger. Replace with any of the following to make
    # the check finish in ~0.15s:
    #     _ = {**v}
    #     _ = list(v.keys())
    #     _ = list(v.items())
    #     _ = v["type"]
    _ = dict(v)
