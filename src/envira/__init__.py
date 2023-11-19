import inspect
from typing import ClassVar, Literal, Optional, Union, get_args, get_origin, Callable, Any
import os

from datetime import datetime


def is_type(type_: type, annot, _) -> bool:
    if len(get_args(annot)) > 0:
        annot_type = get_origin(annot)
    else:
        annot_type = annot
    return annot_type is type_


class Env:
    _handlers: ClassVar[dict[type, Callable]] = {}
    _handlers_detectors: ClassVar[dict[type, Callable[[type, Any, Any], bool]]] = {}

    def __init__(self):
        annotations = {}
        for class_type in type(self).__mro__:
            if not issubclass(class_type, Env):
                break
            annotations.update(inspect.get_annotations(class_type))
        for var, annot in annotations.items():
            if get_origin(annot) is ClassVar:
                continue
            value = os.environ.get(var)
            if getattr(self, var, None) is not None and value is None:
                pass
            else:
                value = self.handle(value, annot)
                setattr(self, var, value)

    def __init_subclass__(cls) -> None:
        cls._handlers = cls._handlers.copy()
        cls._handlers_detectors = cls._handlers_detectors.copy()

    def __repr__(self) -> str:
        annotations = inspect.get_annotations(type(self))
        values = ", ".join([f"{k}={getattr(self, k)}" for k in annotations])
        return f"{type(self).__name__}({values})"

    def __str__(self) -> str:
        return self.__repr__()

    def handle(self, value, annot):
        for type_, detector in self._handlers_detectors.items():
            if detector(type_, annot, value):
                return self._handlers[type_](value, annot, self)
        else:
            return annot(value)

    @classmethod
    def add_handler(
        cls, type_: type, detector: Callable[[type, Any, Any], bool] = is_type
    ):
        def decorator(handler: Callable) -> Callable:
            cls._handlers[type_] = handler
            cls._handlers_detectors[type_] = detector
            return handler

        return decorator


@Env.add_handler(Union)
def union_handler(value: Optional[str], annot, env):
    if value is None or value.lower() in ["none", "null"]:
        return None

    type_, _ = get_args(annot)
    return env.handle(value, type_)


@Env.add_handler(list)
def list_handler(value: str, annot, env):
    values = []
    annot_args = get_args(annot)
    if len(annot_args) == 0:
        type_ = str
    else:
        type_ = annot_args[0]
    for v in value.split(";"):
        values.append(env.handle(v, type_))
    return values


@Env.add_handler(dict)
def dict_handler(value: str, annot, env):
    values = {}
    annot_args = get_args(annot)
    if len(annot_args) == 0:
        key_type, value_type = str, str
    else:
        key_type, value_type = annot_args
    for entry in value.split(","):
        k, v = entry.split("=")
        k = env.handle(k, key_type)
        v = env.handle(v, value_type)
        values[k] = v
    return values


@Env.add_handler(datetime)
def datetime_handler(value: str, _, __):
    if len(set(value) - set('0123456789.')) == 0:
        return datetime.fromtimestamp(float(value))
    else:
        return datetime.fromisoformat(value)


@Env.add_handler(bool)
def bool_handler(value: Optional[str], _, __):
    if value is None:
        return False
    if value.lower() in ["true", "yes", "1"]:
        return True
    if value.lower() in ["false", "no", "0"]:
        return False
    raise ValueError("could not parse bool")


@Env.add_handler(Literal)
def literal_handler(value: str, annot, env: 'Env'):
    for allowed_value in get_args(annot):
        try:
            new_value = env.handle(value, type(allowed_value))
            if new_value == allowed_value:
                return new_value
        except ValueError:
            pass
    raise ValueError("value is not in the allowed values")
