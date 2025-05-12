import pytest

import logctx


def test_log_arguments_basic():
    """Test function argument injection without renaming."""

    @logctx.decorators.log_arguments(["a", "b"])
    def test_function(a, b, c):
        assert logctx.get_current().to_dict() == {"a": a, "b": b}
        return a + b + c

    result = test_function(1, 2, 3)

    # assert input arguments are not altered
    assert result == 6
    # assert context is restored after function call
    assert logctx.get_current().to_dict() == {}


def test_log_arguments_rename():
    """Test function argument injection with renaming."""

    @logctx.decorators.log_arguments(c="d")
    def test_function(a, b, c):
        assert logctx.get_current().to_dict() == {"d": c}
        return a + b + c

    result = test_function(1, 2, 3)

    # assert input arguments are not altered
    assert result == 6
    # assert context is restored after function call
    assert logctx.get_current().to_dict() == {}


def test_log_arguments_mixed():
    """Test function argument injection with and without renaming."""

    @logctx.decorators.log_arguments(["a", "b"], c="d")
    def test_function(a, b, c):
        assert logctx.get_current().to_dict() == {"a": a, "b": b, "d": c}
        return a + b + c

    result = test_function(1, 2, 3)

    # assert input arguments are not altered
    assert result == 6
    # assert context is restored after function call
    assert logctx.get_current().to_dict() == {}


def test_log_arguments_missing_arg():
    """Test function argument injection raises on unrecognized argument."""

    with pytest.raises(ValueError):

        @logctx.decorators.log_arguments(["f"])
        def test_function(a, b, c):
            return a + b + c


def test_log_arguments_missing_kwarg():
    """Test function argument injection raises on unrecognized argument."""

    with pytest.raises(ValueError):

        @logctx.decorators.log_arguments(f="z")
        def test_function(a, b, c):
            return a + b + c
