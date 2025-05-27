import logging

import logctx


def test_filter_with_output_field(caplog):
    logger = logging.getLogger('test_filter_with_output_field')
    logger.setLevel(logging.DEBUG)
    log_filter = logctx.ContextInjectingLoggingFilter(output_field='context_data')
    logger.addFilter(log_filter)

    with logctx.new_context(user='wally'):
        logger.info('Test message')

    assert len(caplog.records) == 1
    for record in caplog.records:
        assert record.levelname == 'INFO'
        assert record.msg == 'Test message'
        assert record.context_data == {'user': 'wally'}


def test_filter_without_output_field(caplog):
    logger = logging.getLogger('test_filter_without_output_field')
    logger.setLevel(logging.DEBUG)
    log_filter = logctx.ContextInjectingLoggingFilter()
    logger.addFilter(log_filter)

    with logctx.new_context(user='wally'):
        logger.info('Test message')

    assert len(caplog.records) == 1
    for record in caplog.records:
        assert record.levelname == 'INFO'
        assert record.msg == 'Test message'
        assert not hasattr(record, 'context_data')
        assert record.user == 'wally'


def test_filter_with_empty_context(caplog):
    logger = logging.getLogger('test_filter_with_empty_context')
    logger.setLevel(logging.DEBUG)
    log_filter = logctx.ContextInjectingLoggingFilter(output_field='context_data')
    logger.addFilter(log_filter)

    logger.info('Test message')

    assert len(caplog.records) == 1
    for record in caplog.records:
        assert record.levelname == 'INFO'
        assert record.msg == 'Test message'
        assert record.context_data == {}


def test_root_included(caplog):
    logger = logging.getLogger('test_root_included')
    logger.setLevel(logging.DEBUG)
    log_filter = logctx.ContextInjectingLoggingFilter(output_field='context_data')
    logger.addFilter(log_filter)

    logctx.root.update(user='root_user')
    with logctx.new_context(foo='bar'):
        logger.info('Root context message')

    assert len(caplog.records) == 1
    for record in caplog.records:
        assert record.levelname == 'INFO'
        assert record.msg == 'Root context message'
        assert record.context_data == {'user': 'root_user', 'foo': 'bar'}


def test_only_root_included(caplog):
    logger = logging.getLogger('test_only_root_included')
    logger.setLevel(logging.DEBUG)
    log_filter = logctx.ContextInjectingLoggingFilter(output_field='context_data')
    logger.addFilter(log_filter)

    logctx.root.update(user='root_user')
    logger.info('Only root context message')

    assert len(caplog.records) == 1
    for record in caplog.records:
        assert record.levelname == 'INFO'
        assert record.msg == 'Only root context message'
        assert record.context_data == {'user': 'root_user'}


def test_root_normal_conflicting_keys(caplog):
    logger = logging.getLogger('test_root_normal_conflicting_keys')
    logger.setLevel(logging.DEBUG)
    log_filter = logctx.ContextInjectingLoggingFilter(output_field='context_data')
    logger.addFilter(log_filter)

    logctx.root.update(user='root_user', session='root_session')
    with logctx.new_context(user='context_user'):
        logger.info('Conflicting keys message')

    assert len(caplog.records) == 1
    for record in caplog.records:
        assert record.levelname == 'INFO'
        assert record.msg == 'Conflicting keys message'
        assert record.context_data == {'user': 'context_user', 'session': 'root_session'}
