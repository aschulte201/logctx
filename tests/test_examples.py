# Assure examples can be run without errors
import importlib

import pytest


@pytest.mark.parametrize(
    'module_name',
    [
        'basics',
        'generators',
        'log_injection',
        'thread_isolation',
        'arguments',
        'root',
    ],
)
def test_examples(module_name):
    importlib.import_module(f'examples.{module_name}')
    # import examples.arguments  # noqa: F401

    # The test will pass if no exceptions are raised during the import
    # and execution of the example code.
    assert True
