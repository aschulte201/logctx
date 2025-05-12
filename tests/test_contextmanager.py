import asyncio
import threading

import pytest

import logctx


def test_context_basic():
    assert logctx.get_current().to_dict() == {}

    with logctx.new_context(user="alice"):
        assert logctx.get_current().to_dict() == {"user": "alice"}

    assert logctx.get_current().to_dict() == {}


def test_context_nested():
    with logctx.new_context(user="alice", role="admin"):
        assert logctx.get_current().to_dict() == {"user": "alice", "role": "admin"}

        with logctx.new_context(role="user"):
            assert logctx.get_current().to_dict() == {"user": "alice", "role": "user"}

        assert logctx.get_current().to_dict() == {"user": "alice", "role": "admin"}

    assert logctx.get_current().to_dict() == {}


def test_context_thread_isolation():
    def thread_func():
        # no context propagation across threads
        assert logctx.get_current().to_dict() == {}
        with logctx.new_context(thread="child"):
            assert logctx.get_current().to_dict() == {"thread": "child"}

    with logctx.new_context(thread="main"):
        thread = threading.Thread(target=thread_func)
        thread.start()
        thread.join()

        assert logctx.get_current().to_dict() == {"thread": "main"}


@pytest.mark.asyncio
async def test_context_async_isolation():
    async def async_func(name):
        with logctx.new_context(user=name):
            await asyncio.sleep(0.01)
            return logctx.get_current().to_dict()

    results = await asyncio.gather(async_func("alice"), async_func("bob"))

    assert len(results) == 2
    assert {"user": "alice"} in results
    assert {"user": "bob"} in results


@pytest.mark.asyncio
async def test_context_persists_across_await():
    async def nested_task():
        await asyncio.sleep(0.01)
        assert logctx.get_current().to_dict() == {"session": "xyz"}

    with logctx.new_context(session="xyz"):
        await nested_task()


def test_context_clear():
    with logctx.new_context(foo="bar"):
        with logctx.new_context(user="alice", role="admin"):
            assert logctx.get_current().to_dict() == {
                "foo": "bar",
                "user": "alice",
                "role": "admin",
            }
            logctx.clear()
            assert logctx.get_current().to_dict() == {}

        assert logctx.get_current().to_dict() == {"foo": "bar"}


def test_context_update():
    with logctx.new_context(foo="bar"):
        with logctx.new_context(user="alice", role="admin"):
            assert logctx.get_current().to_dict() == {
                "foo": "bar",
                "user": "alice",
                "role": "admin",
            }

            logctx.update(user="bob")
            assert logctx.get_current().to_dict() == {
                "foo": "bar",
                "user": "bob",
                "role": "admin",
            }

        assert logctx.get_current().to_dict() == {"foo": "bar"}
