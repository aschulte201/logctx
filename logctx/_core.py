import contextvars
import dataclasses
import logging
from contextlib import contextmanager
from typing import Any, Generator, Mapping, Optional

__all__: list[str] = [
    "LogContext",
    "get_current",
    "new_context",
    "update",
    "clear",
    "ContextInjectingLoggingFilter",
]


@dataclasses.dataclass(frozen=True)
class LogContext:
    """Dataclass holding information about one specific log context.

    This class is used to store key-value pairs that are relevant for the
    current logging context. It is designed to be immutable to prevent
    accidental mutations by users.

    If you want to update the context, use `logctx.update()` or `logctx.new_context()`.

    Attributes:
        data (Mapping[str, Any]): A mapping of key-value pairs representing
            the context data.
    """

    data: Mapping[str, Any] = dataclasses.field(default_factory=dict)

    def with_values(self, **kwargs) -> "LogContext":
        """Create a new context with additional key-value pairs.

        This method returns a new instance of LogContext with the current
        context data merged with the provided key-value pairs. Duplicate keys
        will be overwritten by the new values.

        Caution:
            This method does not affect the current active context, meaning that the
            resulting context will not be included in any log messages.

        Args:
            **kwargs: Key-value pairs to be added to the new context.
        Returns:
            LogContext: A new instance of LogContext with the merged data.
        """

        return LogContext({**self.data, **kwargs})

    def to_dict(self) -> dict[str, Any]:
        """Convert the context to a dictionary."""

        return dict(self.data)


_mdc_context: contextvars.ContextVar[LogContext] = contextvars.ContextVar("_mdc_context")


# TODO: return None or raise on no context
def get_current() -> LogContext:
    """Retrieve current context.

    This function retrieves the current logging context from the context
    variable. If no context is found, it returns an empty LogContext
    instance.

    Returns:
        LogContext: The current logging context.
    """
    try:
        return _mdc_context.get()
    except LookupError:
        return LogContext()


@contextmanager
def new_context(**kwargs) -> Generator[LogContext, None, None]:
    """Create a new context with the provided key-value pairs.

    The new context inherits all key-value pairs from the current context and
    adds the provided pairs. Duplicate keys will be overwritten by the new values.

    Args:
        **kwargs: Key-value pairs to be included in the new context.

    Yields:
        LogContext: The new logging context.
    """

    current_log_ctx: LogContext = get_current()
    new_log_ctx = current_log_ctx.with_values(**kwargs)
    token = _mdc_context.set(new_log_ctx)
    try:
        yield new_log_ctx
    finally:
        _mdc_context.reset(token)


def update(**kwargs) -> LogContext:
    """Append key-value pairs to the current context.

    Duplicate keys will be overwritten by the new values.

    Will not affect log calls in current context made before the update.

    Args:
        **kwargs: Key-value pairs to be added to the current context.

    Returns:
        LogContext: The updated logging context with the appended key-value
            pairs.
    """
    current_log_ctx = get_current()
    updated_log_ctx = current_log_ctx.with_values(**kwargs)
    _mdc_context.set(updated_log_ctx)

    return updated_log_ctx


def clear() -> None:
    """Clear the current context.

    Only affects current context. After leaving current context, the context
    will be reset to its previous state.

    Example:
    ```python
    with logctx.new_context(a=1, b=2):
        with logctx.new_context(c=3):
            # Context is now: {'a': 1, 'b': 2, 'c': 3}
            logctx.clear()
            # Context is now: {}
        # Context is now: {'a': 1, 'b': 2}
    ```
    """
    _mdc_context.set(LogContext())


class ContextInjectingLoggingFilter(logging.Filter):
    """Logging filter that injects the current context into log records.

    Attributes:
        name (str): The name of the filter. This is used to identify the
            filter in the logging system.

        output_field (str): The name of the field in the log record where the
            context data will be injected. If not provided, the context data
            will be injected into the log record as root level attributes.
    """

    def __init__(self, name: str = "", output_field: Optional[str] = None) -> None:
        super().__init__(name=name)
        self._output_field: Optional[str] = output_field

    def filter(self, record: logging.LogRecord) -> bool:
        context: LogContext = get_current()
        if self._output_field is not None:
            setattr(record, self._output_field, context.to_dict())
        else:
            for k, v in context.to_dict().items():
                setattr(record, k, v)
        return True
