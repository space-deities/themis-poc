from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, replace
from enum import Enum, auto
from typing import Any, Optional, Union, cast


# -----------------------------------------------------------------------------
# Enums
# -----------------------------------------------------------------------------
class Operator(Enum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GE = "ge"
    LT = "lt"
    LE = "le"
    BW = "bw"
    NBW = "nbw"

class ValueFmt(Enum):
    ENG = "ENG"
    RAW = "RAW"

class Action(Enum):
    NOACTION = auto()
    ABORT = auto()
    SKIP = auto()
    CANCEL = auto()
    REPEAT = auto()
    RECHECK = auto()
    RESEND = auto()
    RESUME = auto()
    HANDLE = auto()

# -----------------------------------------------------------------------------
# Defaults + Modifiers
# -----------------------------------------------------------------------------
DEFAULTS: dict[str, Any] = {
    "IgnoreCase": False,
    "Retries": 2,
    "Tolerance": 0.0,
    "ValueFormat": ValueFmt.ENG,
    "Wait": False,
    "Timeout": None,
    "Delay": None,
    "AdjLimits": False,

    "OnFalse": {Action.NOACTION},
    "OnTrue": {Action.NOACTION},
    "PromptUser": True,

    "OnFailure": {Action.ABORT, Action.SKIP, Action.REPEAT, Action.CANCEL},
    "PromptFailure": True,
    "HandleError": True,

    "Notify": True,
    "Confirm": False
}

@dataclass(frozen=True)
class Modifiers:
    IgnoreCase: bool = DEFAULTS["IgnoreCase"]
    Retries: int = DEFAULTS["Retries"]
    Tolerance: float = DEFAULTS["Tolerance"]
    ValueFormat: ValueFmt = DEFAULTS["ValueFormat"]
    Wait: bool = DEFAULTS["Wait"]
    Timeout: Optional[float] = DEFAULTS["Timeout"]
    Delay: Optional[float] = DEFAULTS["Delay"]
    AdjLimits: bool = DEFAULTS["AdjLimits"]

    OnFalse: frozenset[Action] = frozenset(DEFAULTS["OnFalse"])
    OnTrue: frozenset[Action] = frozenset(DEFAULTS["OnTrue"])
    PromptUser: bool = DEFAULTS["PromptUser"]

    OnFailure: frozenset[Action] = frozenset(DEFAULTS["OnFailure"])
    PromptFailure: bool = DEFAULTS["PromptFailure"]
    HandleError: bool = DEFAULTS["HandleError"]

    Notify: bool = DEFAULTS["Notify"]
    Confirm: bool = DEFAULTS["Confirm"]

# -----------------------------------------------------------------------------
# Conditions & Boolean expressions
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class Condition:
    left: Any
    op: "Operator"
    right: Any
    overrides: Optional[Modifiers] = None

@dataclass(frozen=True)
class BooleanExpr:
    kind: str  # "AND" | "OR"
    children: list[Union["BooleanExpr", Condition]]

KNOWN_OPS: dict[str, Operator] = {o.value: o for o in Operator}

def _coerce_operator(x: Any) -> Operator:
    if isinstance(x, Operator):
        return x
    if isinstance(x, str) and x.lower() in KNOWN_OPS:
        return KNOWN_OPS[x.lower()]
    raise TypeError(f"Unknown operator: {x!r}")

def _coerce_valuefmt(x: Any) -> ValueFmt:
    if isinstance(x, ValueFmt):
        return x
    if isinstance(x, str):
        u = x.upper()
        if u in ("ENG", "RAW"):
            return ValueFmt[u]
    raise TypeError(f"Unknown ValueFormat: {x!r}")

def _to_action_set(val: Union[Action, Sequence[Action]]) -> frozenset[Action]:
    if isinstance(val, Action):
        return frozenset({val})
    if isinstance(val, (str, bytes)):
        raise TypeError("Action sets must be Action or Iterable[Action], not str/bytes")
    return frozenset(cast(Sequence[Action], val))

def parse_modifiers(
    kwargs: Mapping[str, object],
    base: Optional[Modifiers] = None,
    allowed: Optional[Iterable[str]] = None,
) -> Modifiers:
    """
    Parse ONLY PascalCase keys into a Modifiers object.
    If `allowed` is provided, any PascalCase key not in it triggers a TypeError.
    """
    mods: Modifiers = base if base is not None else Modifiers()

    # Enforce allowlist if provided
    if allowed is not None:
        allowed_set = set(allowed)
        bad = [k for k in kwargs.keys() if k[:1].isupper() and k not in allowed_set]
        if bad:
            raise TypeError(f"Unsupported modifier(s) for this primitive: {sorted(bad)}")

    for k, raw in kwargs.items():
        if not k[:1].isupper():
            # not a modifier key; ignore here (decorator routes non-PascalCase to params)
            continue
        if not hasattr(mods, k):
            raise TypeError(f"Unknown modifier '{k}'")  # not a field in Modifiers

        if k == "ValueFormat":
            v = _coerce_valuefmt(raw)
            mods = replace(mods, ValueFormat=v)
        elif k in {"OnFalse", "OnTrue", "OnFailure"}:
            vset = _to_action_set(cast(Union[Action, Sequence[Action]], raw))
            mods = replace(mods, **{k: vset})
        else:
            mods = replace(mods, **{k: cast(Any, raw)})

    return mods

def parse_condition(raw: Sequence[Any]) -> Condition:
    """Accepts: ['TM', 'eq', value]  or  ['TM', 'eq', value, {Modifier: ...}]"""
    if not (isinstance(raw, (list, tuple)) and len(raw) >= 3):
        raise TypeError(f"Bad condition shape: {raw!r}")
    left, op, right, *rest = raw
    overrides = None
    if rest:
        (maybe_dict,) = rest
        if not isinstance(maybe_dict, dict):
            raise TypeError("Per-condition overrides must be a dict as 4th element")
        overrides = parse_modifiers(cast(Mapping[str, object], maybe_dict))
    return Condition(left=left, op=_coerce_operator(op), right=right, overrides=overrides)

def _to_node(x: Any) -> Union[BooleanExpr, Condition]:
    if isinstance(x, (BooleanExpr, Condition)):
        return x
    if isinstance(x, (list, tuple)):
        return parse_condition(x)
    raise TypeError("AND/OR expect Condition, BooleanExpr, or a raw condition list/tuple")

def AND(*conds: Any) -> BooleanExpr:
    return BooleanExpr("AND", [_to_node(c) for c in conds])

def OR(*conds: Any) -> BooleanExpr:
    return BooleanExpr("OR", [_to_node(c) for c in conds])

def normalize_conditions(arg: Any) -> Union[list[Condition], BooleanExpr]:
    if isinstance(arg, BooleanExpr):
        return arg
    if isinstance(arg, (list, tuple)) and arg and isinstance(arg[0], (list, tuple)):
        return [parse_condition(cast(Sequence[Any], c)) for c in cast(Sequence[Any], arg)]
    if isinstance(arg, (list, tuple)):
        return [parse_condition(cast(Sequence[Any], arg))]
    raise TypeError("Expected a condition, list of conditions, or AND/OR expression")

def merge_mods(base: Modifiers, overrides: Optional[Modifiers]) -> Modifiers:
    if overrides is None:
        return base
    merged: dict[str, Any] = asdict(base)
    for k, v in asdict(overrides).items():
        merged[k] = v
    return Modifiers(**merged)

# -----------------------------------------------------------------------------
# Normalized call & decorator
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class PrimitiveCall:
    spec: Any
    mods: Modifiers
    params: dict[str, Any]

def with_args(
    *,
    base_mods: Optional[Modifiers] = None,
    allowed_modifiers: Optional[Iterable[str]] = None,
):
    """
    Decorator that:
      - routes PascalCase kwargs to Modifiers (validated against `allowed_modifiers` if provided)
      - routes others to params
      - uses first positional as spec
      - calls fn(PrimitiveCall)
    """
    def deco(fn: Callable[[PrimitiveCall], Any]):
        def wrapper(*args: Any, **kwargs: object):
            # split kwargs
            mod_kwargs: dict[str, object] = {k: v for k, v in kwargs.items() if k[:1].isupper()}
            verb_kwargs: dict[str, object] = {k: v for k, v in kwargs.items() if not k[:1].isupper()}

            mods = parse_modifiers(
                mod_kwargs,
                base=base_mods,
                allowed=allowed_modifiers,   # <-- enforce per-primitive allowlist
            )
            spec = args[0] if args else None

            call = PrimitiveCall(spec=spec, mods=mods, params=dict(verb_kwargs))
            return fn(call)
        return wrapper
    return deco

__all__ = [
    "Operator", "ValueFmt", "Action",
    "Modifiers", "Condition", "BooleanExpr",
    "AND", "OR",
    "parse_condition", "normalize_conditions", "merge_mods",
    "PrimitiveCall", "with_args",

]
