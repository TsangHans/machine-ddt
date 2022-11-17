# -*- coding:utf-8 -*-
"""

@Auther: niu
@FileName: abstract.py
@Introduction: 定义抽象类

"""
from __future__ import annotations

from threading import Lock

__all__ = ["SingleMeta"]


class SingleMeta(type):
    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

