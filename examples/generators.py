import logctx


@logctx.decorators.inject_context(generator_context='active')
def my_generator():
    # The context inside the generator execution will include:
    # - the decorator's context
    # - the context of the caller

    for i in range(3):
        print('Context in generator:', logctx.get_current().to_dict())
        # > {'generator_context': 'active', 'user': 'alice'}
        yield i


with logctx.new_context(user='alice'):
    gen = my_generator()

    for value in gen:
        print('Value:', value)

        # The outer context remains unaffected
        print('Context during iteration:', logctx.get_current().to_dict())
        # > {'user': 'alice'}

        print('\n')
