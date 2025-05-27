import pytest

import logctx


def test_capture_and_restore_basic_context():
    propagator = logctx.ContextPropagator()
    with logctx.new_context(a=1):
        propagator.capture_basic()
        
        logctx.update(b=2) # should not be captured
        assert logctx.get_current().to_dict() == {'a': 1, 'b': 2}

    with logctx.new_context():
        assert logctx.get_current().to_dict() == {}
        propagator.restore_basic()
        assert logctx.get_current().to_dict() == {'a': 1}


def test_capture_and_restore_root_context():
    logctx.root.clear()
    logctx.root.update(a=1)
    propagator = logctx.ContextPropagator()
    propagator.capture_root()

    logctx.root.update(b=2) # should not be captured
    assert logctx.root.get_current().to_dict() == {'a': 1, 'b': 2}
    logctx.root.clear()

    propagator.restore_root()
    assert logctx.root.get_current().to_dict() == {'a': 1}


def test_restore_without_capture_raises():
    propagator = logctx.ContextPropagator()
    with pytest.raises(RuntimeError):
        propagator.restore()


def test_restore_outside_context_raises():
    with logctx.new_context(a=1):
        propagator = logctx.ContextPropagator.capture_current()

    with pytest.raises(logctx.NoActiveContextError):
        propagator.restore()    


def test_capture_all_restore_only_root():
    logctx.root.clear()
    logctx.root.update(a=2)
    with logctx.new_context(a=1):
        propagator = logctx.ContextPropagator()
        propagator.capture(capture_basic=True, capture_root=True)

    logctx.root.clear()
    with logctx.new_context():
        propagator.restore(restore_basic=False, restore_root=True)
        assert logctx.root.get_current().to_dict() == {'a': 2}
        assert logctx.get_current().to_dict() == {}
