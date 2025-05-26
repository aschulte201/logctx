import contextvars
import dataclasses
import logging
from contextlib import contextmanager
from typing import Any, Mapping, Optional

__all__: list[str] = [
    'LogContext',
    'get_current',
    'new_context',
    'update',
    'clear',
    'ContextInjectingLoggingFilter',
]


class NoActiveContextError(RuntimeError):
    """Exception raised when there is no active context.

    This exception is raised when an operation that requires an active
    context is attempted, but no context is currently set.
    """


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

    def with_values(self, **kwargs) -> 'LogContext':
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


_context_var: contextvars.ContextVar[LogContext] = contextvars.ContextVar('_context_var')
_root_context_var: contextvars.ContextVar[LogContext] = contextvars.ContextVar(
    '_root_context_var', default=LogContext()
)


class _ContextManager:
    def __init__(self, ctx_var: contextvars.ContextVar[LogContext]):
        self._ctx_var = ctx_var

    def get_current(self) -> LogContext:
        """Retrieve current context.

        This function retrieves the current logging context from the context
        variable. If no context is found, it returns an empty LogContext
        instance.

        Returns:
            LogContext: The current logging context.
        """
        try:
            return self._ctx_var.get()
        except LookupError:
            raise NoActiveContextError(
                'There is no active context. Use new_context() to create one.'
            ) from None

    def update(self, **kwargs):
        """Append key-value pairs to the current context.

        Duplicate keys will be overwritten by the new values.

        Will not affect log calls in current context made before the update.

        Args:
            **kwargs: Key-value pairs to be added to the current context.

        Returns:
            LogContext: The updated logging context with the appended key-value
                pairs.
        """
        current_log_ctx = self.get_current()
        updated_log_ctx = current_log_ctx.with_values(**kwargs)
        self._ctx_var.set(updated_log_ctx)
        return updated_log_ctx

    def clear(self):
        """Clear the current context.

        Only affects current context. After leaving current context, the context
        will be reset to its previous state.

        Previous root context cannot be restored after this.

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
        self.get_current()  # ensure context exists
        self._ctx_var.set(LogContext())


class _NestableContextManager(_ContextManager):
    @contextmanager
    def new_context(self, **kwargs):
        """Create a new context with the provided key-value pairs.

        The new context inherits all key-value pairs from the current context and
        adds the provided pairs. Duplicate keys will be overwritten by the new values.

        Args:
            **kwargs: Key-value pairs to be included in the new context.

        Yields:
            LogContext: The new logging context.
        """
        try:
            current_log_ctx = self.get_current()
            new_log_ctx = current_log_ctx.with_values(**kwargs)

        except NoActiveContextError:
            new_log_ctx = LogContext(data=kwargs)

        token = self._ctx_var.set(new_log_ctx)
        try:
            yield new_log_ctx
        finally:
            self._ctx_var.reset(token)


_context = _NestableContextManager(_context_var)
root = _ContextManager(_root_context_var)
"""Context manager for the root context.

This context manager is used to manage the root logging context, which is
independent of any nested contexts created by the functions of this module.

It allows you to retrieve, update, and clear the root context, but not to create
new nested contexts.
"""

get_current = _context.get_current
new_context = _context.new_context
update = _context.update
clear = _context.clear


class ContextInjectingLoggingFilter(logging.Filter):
    """Logging filter that injects the current context into log records.

    Attributes:
        name (str): The name of the filter. This is used to identify the
            filter in the logging system.

        output_field (str): The name of the field in the log record where the
            context data will be injected. If not provided, the context data
            will be injected into the log record as root level attributes.
    """

    def __init__(self, name: str = '', output_field: Optional[str] = None) -> None:
        super().__init__(name=name)
        self._output_field: Optional[str] = output_field

    def filter(self, record: logging.LogRecord) -> bool:
        root_context = root.get_current()
        try:
            context: LogContext = get_current()
        except NoActiveContextError:
            context = LogContext()

        # current context should overwrite root, as it is further down
        context = root_context.with_values(**context.data)

        if self._output_field is not None:
            setattr(record, self._output_field, context.to_dict())
        else:
            for k, v in context.to_dict().items():
                setattr(record, k, v)
        return True


class ContextPropagator:
    """Enables context propagation across threads / async tasks, ..."""

    def __init__(self):
        self._captured_basic: Optional[LogContext] = None
        self._captured_root: Optional[LogContext] = None
        self._did_capture: bool = False

    @classmethod
    def capture_current(cls) -> 'ContextPropagator':
        """Capture the current context and return a ContextPropagator instance.

        This method captures the current context and returns an instance of
        ContextPropagator that can be used to restore the captured context later.
        """
        propagator = cls()
        propagator.capture(capture_basic=True, caputre_root=True)
        return propagator

    def capture(self, capture_basic: bool = True, caputre_root: bool = True) -> None:
        """Capture the current context.

        Args:
            basic (bool): Whether to capture the basic context (default: True).
            root (bool): Whether to capture the root context (default: True).
        """

        self._did_capture = True

        if capture_basic:
            self._captured_basic = get_current()
        if caputre_root:
            self._captured_root = root.get_current()

    def restore(
        self, restore_basic: Optional[bool] = None, restore_root: Optional[bool] = None
    ) -> None:
        """Restore the captured context.

        Args:
            restore_basic (Optional[bool]): Whether to restore the basic context.
                If None, defaults to True if a basic context was captured.
            restore_root (Optional[bool]): Whether to restore the root context.
                If None, defaults to True if a root context was captured.

        Raises:
            RuntimeError: If no context was captured before calling this method.
        """

        if not self._did_capture:
            raise RuntimeError(
                'Cannot restore context, no context was captured. Call capture() first.'
            )

        should_restore_basic = True if restore_basic is not False else False
        if should_restore_basic and self._captured_basic is not None:
            _context_var.set(self._captured_basic)

        should_restore_root = True if restore_root is not False else False
        if should_restore_root and self._captured_root is not None:
            _root_context_var.set(self._captured_root)
