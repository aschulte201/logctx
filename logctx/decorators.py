"""Decorators for function based context injection.

This module provides decorators for injecting static context or function arguments
into functions and methods.

The decorators automatically create a new context around the
decorated function, including all provided keyword arguments into the new context.
"""

import inspect
from collections.abc import Callable, Generator
from functools import wraps
from typing import AsyncGenerator, Awaitable, Optional, TypeVar

from typing_extensions import ParamSpec

from logctx import _core

_P = ParamSpec("_P")
_R = TypeVar("_R")


def _sync_wrapper(func: Callable[_P, _R], **static_context) -> Callable[_P, _R]:
    """Context wrapper for synchronous functions."""

    @wraps(func)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        with _core.new_context(**static_context):
            return func(*args, **kwargs)

    return wrapper


def _async_wrapper(
    func: Callable[_P, Awaitable[_R]], **static_context
) -> Callable[_P, Awaitable[_R]]:
    """Context wrapper for async functions."""

    @wraps(func)
    async def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        with _core.new_context(**static_context):
            return await func(*args, **kwargs)

    return wrapper


_GenYield = TypeVar("_GenYield")
_GenSend = TypeVar("_GenSend")
_GenReturn = TypeVar("_GenReturn")


def _sync_generator_wrapper(
    func: Callable[_P, Generator[_GenYield, _GenSend, _GenReturn]], **static_context
) -> Callable[_P, Generator[_GenYield, _GenSend, _GenReturn]]:
    """Context wrapper for synchronous generators."""

    @wraps(func)
    def wrapper(
        *args: _P.args, **kwargs: _P.kwargs
    ) -> Generator[_GenYield, _GenSend, _GenReturn]:
        gen = func(*args, **kwargs)
        with _core.new_context(**static_context):
            first_element: _GenYield = next(gen)

        to_send: _GenSend = yield first_element

        while True:
            try:
                with _core.new_context(**static_context):
                    to_yield: _GenYield = gen.send(to_send)

            except StopIteration as e:
                # since PEP 479 generators should gracefully return a value without
                # raising StopIteration.
                return e.value
            else:
                to_send = yield to_yield

    return wrapper


def _async_generator_wrapper(
    func: Callable[_P, AsyncGenerator[_GenYield, _GenSend]], **static_context
):
    @wraps(func)
    async def wrapper(
        *args: _P.args, **kwargs: _P.kwargs
    ) -> AsyncGenerator[_GenYield, _GenSend]:
        gen = func(*args, **kwargs)

        with _core.new_context(**static_context):
            first_element: _GenYield = await gen.__anext__()

        to_send: _GenSend = yield first_element

        while True:
            try:
                with _core.new_context(**static_context):
                    to_yield: _GenYield = await gen.asend(to_send)
            except StopAsyncIteration:
                return
            else:
                to_send = yield to_yield

    return wrapper


def inject_context(**static_context):
    """Decorator injecting static context into a function.

    This decorator will automatically create a new context around the decorated function
    including all provided keyword arguments into the new context.

    Args:
        **static_context: Keyword arguments representing the static context
            to be injected.
    """

    def _decorator(func):
        if inspect.isgeneratorfunction(func):
            return _sync_generator_wrapper(func, **static_context)

        elif inspect.isasyncgenfunction(func):
            return _async_generator_wrapper(func, **static_context)

        elif inspect.iscoroutinefunction(func):
            return _async_wrapper(func, **static_context)

        elif inspect.isfunction(func):
            return _sync_wrapper(func, **static_context)

        else:
            raise TypeError(
                f"Unsupported function type: {type(func)}. "
                "Function must be a coroutine, generator, or regular function."
            )

    return _decorator


def log_arguments(args: Optional[list[str]] = None, **kwargs):
    """Decorator for auto-injecting function arguments into log context.

    This decorator will automatically create a new context around the decorated function
    including specified function arguments into the new context.

    Args:
        args (list[str], optional): A list of function argument names to log.
            Each argument will be injected into the context with its normal key.
        **kwargs: A mapping of function argument names to context keys.

    Raises:
        ValueError: If any specified argument is not found in the function's signature.
    """
    args = args or []

    def decorator(func: Callable[_P, _R]) -> Callable[_P, _R]:
        func_params = inspect.signature(func).parameters
        for arg in args:
            if arg not in func_params:
                raise ValueError(
                    f"Argument '{arg}' not found in the function's signature."
                )
        for arg in kwargs:
            if arg not in func_params:
                raise ValueError(
                    f"Argument '{arg}' not found in the function's signature."
                )

        @wraps(func)
        def wrapper(*func_args: _P.args, **func_kwargs: _P.kwargs) -> _R:
            signature = inspect.signature(func)
            bound = signature.bind(*func_args, **func_kwargs)
            bound.apply_defaults()

            context_data = {}
            for arg in args:
                context_data[arg] = bound.arguments[arg]
            for arg, dest in kwargs.items():
                context_data[dest] = bound.arguments[arg]

            with _core.new_context(**context_data):
                return func(*func_args, **func_kwargs)

        return wrapper

    return decorator
