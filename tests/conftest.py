import pytest

import logctx
import logctx._core


@pytest.fixture(scope='function', autouse=True)
def reset_root_context():
    """Reset root context before each test."""
    logctx._core._root_context_var.set(logctx.LogContext())
