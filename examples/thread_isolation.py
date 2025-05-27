import threading

import logctx

#
#   Isolation Example
#
print('\n\nIsolation Example')
print('----------------------')


@logctx.decorators.inject_context()
# the decorator is required to start a new context other than root
def isolated_thread_func():
    # no context propagation across threads
    print('Context in isolated thread:', logctx.get_current().to_dict())
    # > {}
    print('Root in isolated thread:', logctx.root.get_current().to_dict())
    # > {}

    with logctx.new_context(thread='child'):
        print('Child context in isolated thread:', logctx.get_current().to_dict())
        # > {'thread': 'child'}


with logctx.new_context(thread='main'):
    logctx.root.update(thread_root='main')
    # create & start thread inside active context
    thread = threading.Thread(target=isolated_thread_func)
    thread.start()
    thread.join()

    print('Context outside thread:', logctx.get_current().to_dict())
    # > {'thread': 'main'}
    print('Root outside thread:', logctx.root.get_current().to_dict())
    # > {'thread_root': 'main'}

#
#   Propagation Example
#
print('\n\nPropagation Example')
print('----------------------')


@logctx.decorators.inject_context()
# the decorator is required to start a new context other than root
def propagated_thread_func(ctx_propagator: logctx.ContextPropagator):
    # context is propagated as input argument
    ctx_propagator.restore()
    print('Context in propagated thread:', logctx.get_current().to_dict())
    # > {'thread': 'main'}
    print('Root in propagated thread:', logctx.root.get_current().to_dict())
    # > {'thread_root': 'main'}


with logctx.new_context(thread='main'):
    logctx.root.update(thread_root='main')
    # create & start thread inside active context
    thread = threading.Thread(
        target=propagated_thread_func, args=(logctx.ContextPropagator.capture_current(),)
    )
    thread.start()
    thread.join()

    print('Context outside thread:', logctx.get_current().to_dict())
    # > {'thread': 'main'}
    print('Root outside thread:', logctx.root.get_current().to_dict())
    # > {'thread_root': 'main'}
