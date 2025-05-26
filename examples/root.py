import logctx

#
#   Root decoupling
#
print('\n\nRoot decoupling')
print('----------------------')

print('Root context before:', logctx.root.get_current().to_dict())
# > {}

with logctx.new_context(a=1):
    logctx.root.update(a=2)
    print('Context inside child:', logctx.get_current().to_dict())
    # > {'a': 1}
    print('Root inside child:', logctx.root.get_current().to_dict())
    # > {'a': 2}

    logctx.clear()
    print('Context after clear', logctx.get_current().to_dict())
    # > {}
    print('Root after clear:', logctx.root.get_current().to_dict())
    # > {'a': 2}

print('Root after child:', logctx.root.get_current().to_dict())
# > {'a': 2}
