import logging

import logctx


def test_filter_with_output_field(caplog):
    logger = logging.getLogger("test_filter_with_output_field")
    logger.setLevel(logging.DEBUG)
    log_filter = logctx.ContextInjectingLoggingFilter(output_field="context_data")
    logger.addFilter(log_filter)

    with logctx.new_context(user="wally"):
        logger.info("Test message")

    assert len(caplog.records) == 1
    for record in caplog.records:
        assert record.levelname == "INFO"
        assert record.msg == "Test message"
        assert record.context_data == {"user": "wally"}


def test_filter_without_output_field(caplog):
    logger = logging.getLogger("test_filter_without_output_field")
    logger.setLevel(logging.DEBUG)
    log_filter = logctx.ContextInjectingLoggingFilter()
    logger.addFilter(log_filter)

    with logctx.new_context(user="wally"):
        logger.info("Test message")

    assert len(caplog.records) == 1
    for record in caplog.records:
        assert record.levelname == "INFO"
        assert record.msg == "Test message"
        assert not hasattr(record, "context_data")
        assert record.user == "wally"


def test_filter_with_empty_context(caplog):
    logger = logging.getLogger("test_filter_with_empty_context")
    logger.setLevel(logging.DEBUG)
    log_filter = logctx.ContextInjectingLoggingFilter(output_field="context_data")
    logger.addFilter(log_filter)

    logger.info("Test message")

    assert len(caplog.records) == 1
    for record in caplog.records:
        assert record.levelname == "INFO"
        assert record.msg == "Test message"
        assert record.context_data == {}
