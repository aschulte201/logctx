"""logctx package

This package provides a convenient way to manage logging contexts in Python.

It allows you to manage key-value pairs for log-contexts which can be automatically
added to log messages within their respective context.
"""

__author__ = 'Alexander Schulte'
__maintainer__ = 'Alexander Schulte'
__version__ = "1.0.0"

from logctx import decorators
from logctx._core import (
    ContextInjectingLoggingFilter,
    ContextPropagator,
    LogContext,
    NoActiveContextError,
    clear,
    get_current,
    new_context,
    root,
    update,
)

__all__ = [
    'ContextInjectingLoggingFilter',
    'ContextPropagator',
    'LogContext',
    'clear',
    'get_current',
    'new_context',
    'update',
    'decorators',
    'NoActiveContextError',
    'root',
]
