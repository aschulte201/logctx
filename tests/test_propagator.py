import pytest

import logctx


def test_capture_and_restore_basic_context():
    with logctx.new_context(a=1):
        logctx.update(b=2)
        propagator = logctx.ContextPropagator.capture_current()

        logctx.update(c=3)
        assert logctx.get_current().to_dict() == {'a': 1, 'b': 2, 'c': 3}

        logctx.clear()
        propagator.restore()
        # Should restore to the captured context (a=1, b=2)
        assert logctx.get_current().to_dict() == {'a': 1, 'b': 2}


def test_capture_and_restore_root_context():
    logctx.root.clear()
    logctx.root.update(x=42)
    propagator = logctx.ContextPropagator()
    propagator.capture(capture_basic=False, caputre_root=True)

    logctx.root.update(y=99)
    assert logctx.root.get_current().to_dict() == {'x': 42, 'y': 99}

    logctx.root.clear()
    propagator.restore(restore_basic=False, restore_root=True)
    # Should restore to the captured root context (x=42)
    assert logctx.root.get_current().to_dict() == {'x': 42}


def test_restore_without_capture_raises():
    propagator = logctx.ContextPropagator()
    with pytest.raises(RuntimeError):
        propagator.restore()


def test_capture_and_restore_only_root():
    logctx.root.clear()
    logctx.root.update(a=1)
    propagator = logctx.ContextPropagator()
    propagator.capture(capture_basic=False, caputre_root=True)

    logctx.root.update(a=2)
    propagator.restore(restore_basic=False, restore_root=True)
    assert logctx.root.get_current().to_dict() == {'a': 1}
