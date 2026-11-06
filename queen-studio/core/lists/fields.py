"""A list's fields, read off the model of its items: the answer's fields are the query's (step 6).

Written once, in the model, so what a list answers and what it can be filtered, ordered and selected
by cannot drift apart. A nested model is a field itself, whole, and each of its fields dotted
(`photo`, `photo.status`); a list or a dict is a field only whole. Pure.
"""

from dataclasses import dataclass
from datetime import datetime
from types import NoneType, UnionType
from typing import Annotated, Any, Literal, Union, get_args, get_origin

from pydantic import BaseModel

Kind = Literal["text", "int", "number", "bool", "time", "object", "list"]

_SCALARS: dict[Any, Kind] = {
    str: "text",
    int: "int",
    float: "number",
    bool: "bool",
    datetime: "time",
}


@dataclass(frozen=True)
class ListField:
    name: str  # as the query names it, dotted
    kind: Kind
    allowed: tuple[str, ...] = ()  # a Literal's values; empty when any text goes


def fields_of(model: type[BaseModel], prefix: str = "") -> dict[str, ListField]:
    """Every field of the model, nested ones dotted, in the model's order.

    Raises ValueError for a field the query cannot read, naming it: met when the list is declared.
    """
    found: dict[str, ListField] = {}
    for name, info in model.model_fields.items():
        where = f"{model.__name__}.{name}"
        if info.alias is not None or info.serialization_alias is not None:
            raise ValueError(f"{where}: a list's records are named by their fields, not aliases.")
        path = prefix + name
        kind = _held(info.annotation, where)
        if isinstance(kind, type) and issubclass(kind, BaseModel):
            found[path] = ListField(path, "object")
            found.update(fields_of(kind, path + "."))
        else:
            found[path] = _field(path, kind, where)
    return found


def _held(annotation: Any, where: str) -> Any:
    """What a field holds: `X | None` and `Annotated[X, ...]` are X."""
    if get_origin(annotation) is Annotated:
        return _held(get_args(annotation)[0], where)
    if get_origin(annotation) in (Union, UnionType):
        kinds = [part for part in get_args(annotation) if part is not NoneType]
        if len(kinds) != 1:
            raise ValueError(f"{where}: a list query reads one kind per field, not {annotation}.")
        return _held(kinds[0], where)
    return annotation


def _field(path: str, kind: Any, where: str) -> ListField:
    if kind in _SCALARS:
        return ListField(path, _SCALARS[kind])
    origin = get_origin(kind)
    if origin is Literal:
        values = get_args(kind)
        if all(isinstance(value, str) for value in values):
            return ListField(path, "text", tuple(values))
    if kind in (list, tuple) or origin in (list, tuple):
        return ListField(path, "list")
    if kind is dict or origin is dict:
        return ListField(path, "object")
    raise ValueError(f"{where}: a list query cannot read {kind}.")
