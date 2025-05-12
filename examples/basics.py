import logctx

#
#   Update thorugh child context
#
print('\n\nUpdate through child context')
print('----------------------')

with logctx.new_context(user='alice', role='admin'):
    print('Parent context 1:', logctx.get_current().to_dict())
    # > {'user': 'alice', 'role': 'admin'}

    with logctx.new_context(role='user'):  # role gets overridden
        print('Child context:', logctx.get_current().to_dict())
        # > {'user': 'alice', 'role': 'user'}

    # previous context is restored
    print('Parent context 2:', logctx.get_current().to_dict())
    # > {'user': 'alice', 'role': 'admin'}

print('Root context:', logctx.get_current().to_dict())
# > {}


#
#   Update through .update()
#
print('\n\nUpdate through .update()')
print('----------------------')

with logctx.new_context(user='alice', role='admin'):
    print('Context before update:', logctx.get_current().to_dict())
    # > {'user': 'alice', 'role': 'admin'}

    logctx.update(role='user')  # role gets overridden

    print('Context after update:', logctx.get_current().to_dict())
    # > {'user': 'alice', 'role': 'user'}


#
#  Update through .clear()
#
print('\n\nUpdate through .clear()')
print('----------------------')

with logctx.new_context(user='alice', role='admin'):
    with logctx.new_context(id='foo'):
        print('Context inside child before clear:', logctx.get_current().to_dict())
        # > {'user': 'alice', 'role': 'admin', 'id': 'foo'}

        logctx.clear()  # clears all context

        print('Context inside child after clear:', logctx.get_current().to_dict())
        # > {}

    # context restoration after leaving scope of context that called .clear()
    print('Context in parent after clear:', logctx.get_current().to_dict())
    # > {'user': 'alice', 'role': 'admin'}
