from typing import TypeVar, Callable
from threading import Lock, get_native_id

_T = TypeVar("_T")


class Reference[_T]:
    _value: _T
    _Lset: Lock

    def __init__(self, value: _T) -> None:
        self._value = value
        self._Lset = Lock()

    def get(self) -> _T:
        return self._value

    def set(self, value) -> None:
        self._Lset.acquire()
        self._value = value
        self._Lset.release()

    @property
    def value(self) -> _T:
        return self.get()

    @value.setter
    def value(self, value: _T):
        self.set(value)


class InitOnUse[_T](Reference[_T]):

    _isInit: bool
    _init: Callable[[], _T]
    _Linit: Lock

    def __init__(self, init: Callable[[], _T]) -> None:
        self._isInit = False
        self._init = init
        self._Lset = Lock()
        self._Linit = Lock()

    def get(self) -> _T:
        self._Linit.acquire()
        if not self._isInit:
            self.set(self._init())
        self._Linit.release()
        return super().get()

    def set(self, value):
        super().set(value)
        self._isInit = True


class MultiThread[_T](Reference[_T]):

    _i: Callable[[], _T]
    _d: dict[int, _T]

    def __init__(self, init: Callable[[], _T]) -> None:
        self._d = {}
        self._i = init
        self._Lset = Lock()

    def get(self) -> _T:
        with self._Lset:
            tid = get_native_id()
            if tid in self._d:
                return self._d[tid]
            else:
                obj = self._i()
                self._d[tid] = obj
                return obj

    def set(self, value) -> None:
        with self._Lset:
            tid = get_native_id()
            self._d[tid] = value

    def reset(self) -> None:
        with self._Lset:
            tid = get_native_id()
            if tid in self._d:
                del self._d[tid]
