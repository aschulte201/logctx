import pytest

import logctx


def test_get_current_raises_no_active_context_error():
    with pytest.raises(logctx.NoActiveContextError):
        logctx.get_current()

    with logctx.new_context():
        logctx.get_current()


def test_update_only_in_active_context():
    with pytest.raises(logctx.NoActiveContextError):
        logctx.update(a=1, b=2)

    with logctx.new_context(a=1, b=2):
        logctx.update(c=3)
        assert logctx.get_current().data == {'a': 1, 'b': 2, 'c': 3}

    with pytest.raises(logctx.NoActiveContextError):
        logctx.update(a=1, b=2)


def test_clear_not_creates_context():
    with pytest.raises(logctx.NoActiveContextError):
        logctx.clear()

    with pytest.raises(logctx.NoActiveContextError):
        logctx.get_current()


def test_root_context_unaffected():
    assert logctx.root.get_current().data == {}

    with logctx.new_context(a=1, b=2):
        assert logctx.get_current().data == {'a': 1, 'b': 2}
        assert logctx.root.get_current().data == {}

    assert logctx.root.get_current().data == {}


def test_root_context_isolation():
    assert logctx.root.get_current().data == {}

    with logctx.new_context(a=1):
        logctx.root.update(a=2)
        assert logctx.get_current().data == {'a': 1}
        assert logctx.root.get_current().data == {'a': 2}

        logctx.clear()
        assert logctx.get_current().data == {}
        assert logctx.root.get_current().data == {'a': 2}

    assert logctx.root.get_current().data == {'a': 2}
