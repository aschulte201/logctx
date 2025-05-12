# Logctx

[![CICD](https://github.com/aschulte201/logctx/actions/workflows/cicd.yml/badge.svg?branch=main)](https://github.com/aschulte201/logctx/actions/workflows/cicd.yml)
![PyPI - Status](https://img.shields.io/pypi/status/logctx)
![PyPI - Version](https://img.shields.io/pypi/v/logctx)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/logctx)

![PyPI - License](https://img.shields.io/pypi/l/logctx)
![PyPI - Types](https://img.shields.io/pypi/types/logctx)
![PyPI - Downloads](https://img.shields.io/pypi/dm/logctx)

**Logctx** is a lightweight Python library that enhances logging with contextual information — useful for debugging, tracing, and observability. It integrates seamlessly with Python's built-in `logging` module and supports context management via decorators or context managers.


## 🚀 Features

- **Automatic Context Injection**: Seamlessly inject context into log messages using Python's logging framework.
- **Scoped Contexts**: Define context with decorators or context managers, supporting nested and inherited contexts.
- **Argument Logging**: Automatically log function arguments as part of the context.
- **Runtime Context Manipulation**: Update or clear contexts dynamically during runtime.
- **Thread and Async Safety**: Supports threading and async.


## 📦 Installation

```bash
pip install logctx
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add logctx
```

## ⚡ Quick Start

*Minimal usage example to get started. More information down below.*

```python
import logging

import logctx

# Setup log injection
root_logger = logging.getLogger()
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s %(logctx)s')
context_filter = ContextInjectingLoggingFilter(output_field='logctx')
console_handler.setFormatter(formatter)
console_handler.addFilter(context_filter)
root_logger.addHandler(console_handler)
root_logger.setLevel(logging.DEBUG)

# Usage example
with new_context(user='alice'):
    root_logger.info('User logged in') # > User logged in {'user': 'alice'}
```

## 🧠 How It Works

Contexts are key-value pairs bound to a specific scope using [context managers](#context-managers) or [decorators](#decorators). These contexts are automatically included in log messages, providing additional information alongside the normal log content.

Contexts can also be nested, meaning that inner contexts inherit and may override key-value pairs from outer contexts.

## 🛠️ Context Managers

Use `logctx.new_context()` to create a new context:

```python
import logctx

with logctx.new_context(user="alice", request_id="abc123"):
    # Each log message inside this context manager
    # now additionally carries the user and request_id.
    pass
```

You can inspect the current context using:

```python
print(logctx.get_current().to_dict())
```

## 🎯 Decorators

### Static Context

Use `@logctx.decorators.inject_context()` to add static context to your functions.

***Supports (sync & async):*** *functions, generators, classmethods, instancemethods* 

```python
import logctx

@logctx.decorators.inject_context(fn="my_function")
def my_function():
    print(logctx.get_current().to_dict())  # {'fn': 'my_function'}
```

#### *Special Case: Generators*

```python
import logctx

@logctx.decorators.inject_context(inside=True)
def my_generator():
    # The context inside the generator execution will inherit 
    # the context that was active during initialization of 
    # the generator ({'inside': False, 'foo': 'bar'}),
    # BUT uses its own contexts (from the decorator or created inside) 
    # as child contexts. Hence the overridden inside attribute.
    print(logctx.get_current().to_dict()) # {'inside': True, 'foo': 'bar'}
    yield

with logctx.new_context(inside=False, foo="bar"):
    gen = my_generator()
    for _ in gen():
        print(logctx.get_current().to_dict()) # {'inside': False, 'foo': 'bar'}
```

---

### Argument Logging

Automatically log function arguments as part of the context:

***Supports:*** *functions, classmethods, instancemethods*

***Note***: Does not work properly with generator or async functions.

```python
import logctx

# -> log arguments a and b as is, rename c to d
@logctx.decorators.log_arguments(args=["a", "b"], c="d")
def my_function(a, b, c):
    print(logctx.get_current().to_dict())  # {'a': 1, 'b': 2, 'd': 3}

my_function(1, 2, 3)
```

If one of the specified arguments is not found in the function signature during initialization, a `ValueError` will be raised. This also implicates that an extraction from `*args` or `**kwargs` is not possible.

## 🔄 Manipulating Contexts

*Please note that the context attributes should never be updated directly through instances of `LogContext` (the return values of e.g. the contextmanagers and `logctx.get_current()`).*

Below context manipulation functions work for contexts created by contextmanagers as well as context created by decorators. Use these to alter your current active context.

---

### Updating Contexts

You can add or alter attributes of the current context by calling `logctx.update()`:

```python
import logctx

with logctx.new_context(section="main"):
    logctx.update(request_id="network_request_id")
    print(logctx.get_current().to_dict())  # {'section': 'main', 'request_id': 'network_request_id'}
```

*Warning*: Calling this method without an active context will change your root context, which may cause unexpected side effects. To reset your root context, use [`logctx.clear`](#clearing-contexts) without an active context present.

---

### Clearing Contexts

Clear the current context with `logctx.clear()`:

```python
import logctx

with logctx.new_context(section="main"):
    logctx.clear()
    print(logctx.get_current().to_dict())  # {}
```

Clearing a context will affect **all** key-value pairs of all contexts in scope, but the clearance will only last for the current active scope. After leaving the current scope, the context gets reset to its state before the leaving scope, essentially restoring some of its variables:

```python
import logctx

with logctx.new_context(section="main"):
    with logctx.new_context(user="alice"):
        logctx.get_current().to_dict() # {'section': 'main', 'user': 'alice'}
        logctx.clear()
        logctx.get_current().to_dict() # {}
    
    logctx.get_current().to_dict() # {'section': 'main'}
```

## 🧩 Log Injection

Context gets injected into log messages with [filter objects](https://docs.python.org/3/library/logging.html#filter-objects) from Python's built-in logging module.

Configure your logger to include the context:

```python
import logging

from pythonjsonlogger import jsonlogger
import logctx

# Configure logging
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter("%(message)s %(logctx)s")
handler.setFormatter(formatter)
handler.addFilter(logctx.ContextInjectingLoggingFilter(output_field="logctx"))
# output_field may be ommitted, which injects all context attributes at the root level of the log records.

logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Inject context
with logctx.new_context(user="alice", request_id="abc123"):
    logger.info("User logged in")

# Output:
# {"message": "User logged in", "logctx": {"user": "alice", "request_id": "abc123"}}
```

*Note: This example uses [python-json-logger](https://github.com/madzak/python-json-logger) for better log formats.*


## 🤝 Contributing

Contributions and feedback are welcome! Please reach out to me through issues or else before opening a pull request.

Thanks.

## 📚 See Also

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [pythonjsonlogger](https://github.com/madzak/python-json-logger)