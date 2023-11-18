from abc import ABC, abstractmethod
import inspect
from typing import  Optional, Union, get_args, get_origin
import os

class Handler(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def convert(self, value, annot, env: 'Env'):
        pass

    def detect(self, value, annot, env: 'Env') -> bool:
        return True


class Env:
    def __init__(self):
        annotations = inspect.get_annotations(type(self))
        self.handlers = self._get_all_handlers()

        for var, annot in annotations.items():
            value = os.environ.get(var)
            value = self.handle(value, annot)
            setattr(self, var, value)

    def __repr__(self) -> str:
        annotations = inspect.get_annotations(type(self))
        values = ", ".join([f"{k}={getattr(self, k)}" for k in annotations])
        return f"{type(self).__name__}({values})"

    def __str__(self) -> str:
        return self.__repr__()

    def handle(self, value, annot):
        for handler in self.handlers:
            if handler.detect(value, annot, self):
                value = handler.convert(value, annot, self)
                break
        else:
            value = annot(value)
        return value


    def _get_all_handlers(self):
        handlers: list[Handler] = []
        for attribute in dir(self):
            if attribute in ['_get_all_handlers']:
                continue
            obj = getattr(self, attribute)
            try:
                is_handler = issubclass(obj, Handler)
            except TypeError:
                is_handler = False
            if is_handler:
                handlers.append(obj())

        return handlers

    class OptionalHandler(Handler):
        def convert(self, value: Optional[str], annot, env):
            if value is None or value.lower() == "none":
                return None

            type_, _ = get_args(annot)
            return env.handle(value, type_)

        def detect(self, value, annot, env) -> bool:
            if get_origin(annot) is Union:
                return type(None) in get_args(annot)

            return False

    class ListHandler(Handler):
        def convert(self, value: str, annot, env):
            values = []
            type_ = get_args(annot)[0]
            for v in value.split(";"):
                values.append(env.handle(v, type_))
            return values

        def detect(self, value, annot, env: 'Env') -> bool:
            return isinstance(value, str) and get_origin(annot) is list

    class DictHandler(Handler):
        def convert(self, value: str, annot, env):
            values = {}
            key_type, value_type = get_args(annot)
            for entry in value.split(","):
                k, v = entry.split("=")
                k = env.handle(k, key_type)
                v = env.handle(v, value_type)
                values[k] = v
            return values

        def detect(self, value, annot, env: 'Env') -> bool:
            return isinstance(value, str) and get_origin(annot) is dict


class MyEnv(Env):
    TEST_A: Optional[int]
    TEST_B: int
    TEST_C: list[int]
    TEST_D: dict[str, int]



print(MyEnv())
