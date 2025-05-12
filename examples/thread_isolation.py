import threading

import logctx

#
#   Isolation Example
#
print('\n\nIsolation Example')
print('----------------------')


def isolated_thread_func():
    # no context propagation across threads
    print('Context in isolated thread:', logctx.get_current().to_dict())
    # > {}

    with logctx.new_context(thread='child'):
        print('Child context in isolated thread:', logctx.get_current().to_dict())
        # > {'thread': 'child'}


with logctx.new_context(thread='main'):
    # create & start thread inside active context
    thread = threading.Thread(target=isolated_thread_func)
    thread.start()
    thread.join()

    print('Context outside thread:', logctx.get_current().to_dict())
    # > {'thread': 'main'}

#
#   Propagation Example
#
print('\n\nPropagation Example')
print('----------------------')


@logctx.decorators.inject_context()
# the decorator is recommended to avoid manipulating root context
# for this thread.
def propagated_thread_func(ctx: logctx.LogContext):
    # context is propagated as input argument
    logctx.update(**ctx.to_dict())
    print('Context in propagated thread:', logctx.get_current().to_dict())
    # > {'thread': 'main'}


with logctx.new_context(thread='main'):
    # create & start thread inside active context
    thread = threading.Thread(target=propagated_thread_func, args=(logctx.get_current(),))
    thread.start()
    thread.join()

    print('Context outside thread:', logctx.get_current().to_dict())
    # > {'thread': 'main'}
