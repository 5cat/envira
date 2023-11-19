from typing import Literal, Optional
from envira import Env

from enum import Enum
from datetime import datetime


def test_int(monkeypatch):
    monkeypatch.setenv("A", "123")

    class MyEnv(Env):
        A: int

    my_env = MyEnv()

    assert my_env.A == 123 and isinstance(my_env.A, int)


def test_float(monkeypatch):
    monkeypatch.setenv("A", "23.01")

    class MyEnv(Env):
        A: float

    my_env = MyEnv()

    assert my_env.A == 23.01 and isinstance(my_env.A, float)


def test_str(monkeypatch):
    monkeypatch.setenv("A", "hohoho")

    class MyEnv(Env):
        A: str

    my_env = MyEnv()

    assert my_env.A == "hohoho"


def test_optional_none():
    class MyEnv(Env):
        A: Optional[str]

    my_env = MyEnv()

    assert my_env.A is None


def test_optional_none_explicit(monkeypatch):
    class MyEnv(Env):
        A: Optional[str]

    monkeypatch.setenv("A", "none")

    my_env = MyEnv()

    assert my_env.A is None

    monkeypatch.setenv("A", "null")
    my_env = MyEnv()
    assert my_env.A is None


def test_optional(monkeypatch):
    monkeypatch.setenv("A", "aa")

    class MyEnv(Env):
        A: Optional[str]

    my_env = MyEnv()

    assert my_env.A == "aa"


def test_list(monkeypatch):
    monkeypatch.setenv("A", "1;a;3")

    class MyEnv(Env):
        A: list

    my_env = MyEnv()

    assert my_env.A == ["1", "a", "3"]


def test_list_int(monkeypatch):
    monkeypatch.setenv("A", "1;2;3")

    class MyEnv(Env):
        A: list[int]

    my_env = MyEnv()

    assert my_env.A == [1, 2, 3]


def test_dict(monkeypatch):
    monkeypatch.setenv("A", "a=e,b=c")

    class MyEnv(Env):
        A: dict

    my_env = MyEnv()

    assert my_env.A == {"a": "e", "b": "c"}


def test_dict_int_float(monkeypatch):
    monkeypatch.setenv("A", "1=32.5,7=5.63")

    class MyEnv(Env):
        A: dict[int, float]

    my_env = MyEnv()

    assert my_env.A == {1: 32.5, 7: 5.63}


def test_int_default():
    class MyEnv(Env):
        A: int = 654

    my_env = MyEnv()

    assert my_env.A == 654


def test_optional_int_default():
    class MyEnv(Env):
        A: Optional[int] = None

    my_env = MyEnv()

    assert my_env.A is None


def test_enum(monkeypatch):
    monkeypatch.setenv("A", "0")
    monkeypatch.setenv("B", "1")

    class MyEnum(Enum):
        X = "0"
        Y = "1"

    class MyEnv(Env):
        A: MyEnum
        B: MyEnum

    my_env = MyEnv()
    assert my_env.A is MyEnum.X
    assert my_env.B is MyEnum.Y


def test_datetime_iso(monkeypatch):
    datetime_value = "2023-11-19T19:43:23.023535"
    monkeypatch.setenv("A", datetime_value)

    class MyEnv(Env):
        A: datetime

    my_env = MyEnv()
    assert my_env.A == datetime.fromisoformat(datetime_value)


def test_datetime_timestamp(monkeypatch):
    datetime_value = "1700394203.023535"
    monkeypatch.setenv("A", datetime_value)

    class MyEnv(Env):
        A: datetime

    my_env = MyEnv()
    assert my_env.A == datetime.fromtimestamp(float(datetime_value))


def test_bool_true(monkeypatch):
    monkeypatch.setenv("A", "TRUE")
    monkeypatch.setenv("B", "true")
    monkeypatch.setenv("C", "True")

    class MyEnv(Env):
        A: bool
        B: bool
        C: bool

    my_env = MyEnv()
    assert my_env.A == True
    assert my_env.B == True
    assert my_env.C == True


def test_bool_false(monkeypatch):
    monkeypatch.setenv("A", "FALSE")
    monkeypatch.setenv("B", "false")
    monkeypatch.setenv("C", "False")

    class MyEnv(Env):
        A: bool
        B: bool
        C: bool

    my_env = MyEnv()
    assert my_env.A == False
    assert my_env.B == False
    assert my_env.C == False


def test_bool_empty():
    class MyEnv(Env):
        A: bool

    my_env = MyEnv()
    assert my_env.A == False


def test_literal(monkeypatch):
    monkeypatch.setenv("A", "DEBUG")
    monkeypatch.setenv("B", "1")

    class MyEnv(Env):
        A: Literal["DEBUG", "INFO", "WARN", "ERROR"]
        B: Literal[0, 1]
        C: Literal[False, "s"]

    my_env = MyEnv()

    assert my_env.A == "DEBUG"
    assert my_env.B == 1
    assert my_env.C == False

    monkeypatch.setenv("A", "WARN")
    monkeypatch.setenv("B", "0")
    monkeypatch.setenv("C", "s")

    my_env = MyEnv()

    assert my_env.A == "WARN"
    assert my_env.B == 0
    assert my_env.C == "s"

    class MyEnv2(Env):
        D: Literal[None, 64]

    my_env = MyEnv2()

    assert my_env.D is None

    monkeypatch.setenv("D", "64")
    my_env = MyEnv2()
    assert my_env.D == 64

    monkeypatch.setenv("D", "null")
    my_env = MyEnv2()
    assert my_env.D is None


def test_prefix(monkeypatch):
    monkeypatch.setenv("APP_A", "65")

    class MyEnv(Env):
        A: int

    my_env = MyEnv(prefix="APP_")

    assert my_env.A == 65
