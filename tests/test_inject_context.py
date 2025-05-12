import pytest

import logctx


def test_inject_context_basic():
    @logctx.decorators.inject_context(foo="bar")
    def test_function():
        assert logctx.get_current().to_dict() == {"foo": "bar"}

    test_function()

    assert logctx.get_current().to_dict() == {}


@pytest.mark.asyncio
async def test_inject_context_async():
    """Test @inject_context decorator with async function."""

    @logctx.decorators.inject_context(foo="bar")
    async def test_function():
        assert logctx.get_current().to_dict() == {"foo": "bar"}

    await test_function()

    assert logctx.get_current().to_dict() == {}


def test_inject_context_generator_basic():
    """Test @inject_context decorator with simple generator."""
    context_in_generator = {}

    @logctx.decorators.inject_context(inside=True)
    def basic_generator():
        # The context inside the generator execution should always have inside set to True
        for i in range(5):  # 5 is arbitrary
            assert logctx.get_current().to_dict() == context_in_generator
            yield i

    # Test 1: Simple generator context
    context_in_generator = {"inside": True}
    assert [x for x in basic_generator()] == list(range(5))

    # Test 2: Test generator context with outer context
    # Inside generator execution foo should be set to bar, while inside remains True
    # from the decorator of the generator.
    context_in_generator = {"inside": True, "foo": "bar"}
    with logctx.new_context(inside=False, foo="bar"):
        for _ in basic_generator():
            # Outside generator execution inside should be set to False
            assert logctx.get_current().to_dict() == {"inside": False, "foo": "bar"}

        # Final check to ensure outer context is intact
        assert logctx.get_current().to_dict() == {"foo": "bar", "inside": False}


def test_inject_context_generator_complex():
    """Test @inject_context decorator with complex generator using send and return."""

    context_in_generator = {}

    @logctx.decorators.inject_context(inside=True)
    def complex_generator():
        """Yields letters from the string "abc" and joins input words with a space.

        Yields:
            str: The next letter in the string "abc".

        Returns:
            str: A sentence formed by joining the words sent to
                the generator with a space.
        """

        assert logctx.get_current().to_dict() == context_in_generator

        sentence = []
        for letter in "abc":
            word = yield letter
            sentence.append(word)

        return " ".join(sentence)

    gen = complex_generator()

    # Inside generator execution foo should be set to bar, while inside remains True
    # from the decorator of the generator.
    context_in_generator = {"inside": True, "foo": "bar"}
    with logctx.new_context(inside=False, foo="bar"):
        letter = next(gen)
        while True:
            try:
                assert logctx.get_current().to_dict() == {"inside": False, "foo": "bar"}
                letter = gen.send(letter + "+")
            except StopIteration as e:
                # assert return value of generator remains intact
                assert e.value == "a+ b+ c+"
                break


@pytest.mark.asyncio
async def test_inject_context_async_generator():
    """Same as test_inject_context_generator but for async generator."""
    context_in_generator = {}

    # Define the async generator
    @logctx.decorators.inject_context(inside=True)
    async def async_generator():
        # The context inside the generator execution should always have inside set to True
        for i in range(5):  # 5 is arbitrary
            # The context should always have inside set to True
            assert logctx.get_current().to_dict() == context_in_generator
            yield i

    # Test 1: Simple generator context
    context_in_generator = {"inside": True}
    assert [x async for x in async_generator()] == list(range(5))

    # Test 2: Test generator context with outer context
    # Inside generator execution foo should be set to bar, while inside remains True
    # from the decorator of the generator.
    context_in_generator = {"inside": True, "foo": "bar"}
    with logctx.new_context(inside=False, foo="bar"):
        async for _ in async_generator():
            # Outside generator execution inside should be set to False
            assert logctx.get_current().to_dict() == {"inside": False, "foo": "bar"}

        # Final check to ensure outer context is intact
        assert logctx.get_current().to_dict() == {"foo": "bar", "inside": False}


def test_inject_context_instance_method():
    """Test @inject_context decorator with instance method."""

    class TestClass:
        def __init__(self):
            self.foo = "bar"

        @logctx.decorators.inject_context(inside=True)
        def instance_method(self):
            assert self.foo == "bar"  # assert self preservation
            assert logctx.get_current().to_dict() == {"inside": True, "foo": "bar"}
            return "Hello, World!"

    with logctx.new_context(inside=False, foo="bar"):
        obj = TestClass()
        assert obj.instance_method() == "Hello, World!"
        assert logctx.get_current().to_dict() == {"inside": False, "foo": "bar"}


def test_inject_context_class_method():
    """Test @inject_context decorator with class method."""

    class TestClass:
        foo = "bar"

        @classmethod
        @logctx.decorators.inject_context(inside=True)
        def class_method(cls):
            assert cls.foo == "bar"  # assert cls preservation
            assert logctx.get_current().to_dict() == {"inside": True, "foo": "bar"}
            return "Hello, World!"

    with logctx.new_context(inside=False, foo="bar"):
        assert TestClass.class_method() == "Hello, World!"
        assert logctx.get_current().to_dict() == {"inside": False, "foo": "bar"}


def test_inject_context_static_method():
    """Test @inject_context decorator with static method."""

    class TestClass:
        @staticmethod
        @logctx.decorators.inject_context(inside=True)
        def static_method():
            assert logctx.get_current().to_dict() == {"inside": True, "foo": "bar"}
            return "Hello, World!"

    with logctx.new_context(inside=False, foo="bar"):
        assert TestClass.static_method() == "Hello, World!"
        assert logctx.get_current().to_dict() == {"inside": False, "foo": "bar"}


def test_inject_context_unsupported_type():
    """Test @inject_context decorator with unsupported type."""

    with pytest.raises(TypeError):

        @logctx.decorators.inject_context(inside=True)
        class TestClass: ...
